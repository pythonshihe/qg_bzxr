# -*- coding: utf-8 -*-
import hashlib
import json
import re
import scrapy
from work_utils.get_code import check_code
from work_utils.search_data import search_result
from work_utils.deal_str import deal_str
from work_utils.get_db_company import get_keyword
import time
import logging

logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.INFO)


class BzxrSpiderSpider(scrapy.Spider):
    name = 'bzxr_company'

    # allowed_domains = ['zxgk.court.gov.cn']
    # start_urls = ['http://zxgk.court.gov.cn/']

    def get_md5(self, string):
        code_data = string.encode("utf-8")
        m = hashlib.md5()
        m.update(code_data)
        return m.hexdigest()

    def id_md5(self, name, cf_wsh):
        # print('主体：%s,文书号：%s,内容：%s' % (name, cf_wsh, content))
        cf_wsh = re.sub(r'\(|\)|（|）|号', '', cf_wsh)
        name = re.sub(r'\W|\s', '', name)
        sj_type = '63'
        string_id = sj_type + name + cf_wsh
        md5_id = self.get_md5(string_id)
        return md5_id

    def start_requests(self):
        all_key = get_keyword()
        for key_word in all_key:
            word = key_word[0]
            key_words = word[0:2]
            url = 'http://zxgk.court.gov.cn/zhixing/searchBzxr.do'
            code_dict = check_code()
            codes = code_dict.get('codes')
            codes_id = code_dict.get('codes_id')
            # key_words = '北京'
            form_data = {
                "pName": key_words,
                "pCardNum": "",
                "selectCourtId": "0",
                "pCode": codes,
                "captchaId": codes_id,
                "searchCourtName": "全国法院（包含地方各级法院）",
                "selectCourtArrange": "1",
                "currentPage": "1",
            }
            meta = {"pName": key_words, 'codes': codes, 'codes_id': codes_id}
            yield scrapy.FormRequest(url=url, formdata=form_data, callback=self.page_parse, dont_filter=True, meta=meta)

    def page_parse(self, response):
        codes = response.meta.get('codes')
        codes_id = response.meta.get('codes_id')
        content = response.text
        # print(response.meta)
        content_dict = json.loads(content)[0]
        total_size = content_dict.get('totalSize')  # 总共有多少数据
        current_page = content_dict.get('currentPage')  # 当前页
        if total_size > 0:
            content_list = content_dict.get('result')
            for each_content in content_list:
                # 获取主体和案号md5生成去重id
                oname = each_content.get('pname')
                cf_wsh = each_content.get('caseCode', '')
                md5_id = self.id_md5(oname, cf_wsh)
                data_result = search_result(md5_id)  # 排重id查询结果
                data_id = each_content.get('id', '')
                if not data_result:  # 判断es数据库有无此数据
                    xq_url = 'http://zxgk.court.gov.cn/zhixing/newdetail?id={}&j_captcha={}&captchaId={}'.format(
                        data_id, codes, codes_id)
                    yield scrapy.Request(url=xq_url, callback=self.parse_data, meta={'ws_pc_id': md5_id})
            total_page = content_dict.get('totalPage')  # 总共有多少页
            # print('总页码数：%s' % total_page)
            print('当前页码数：%s' % current_page)
            if total_page > current_page:
                p_name = response.meta.get('pName')  # 获取关键词
                current_page += 1  # 页码+1
                url = 'http://zxgk.court.gov.cn/zhixing/searchBzxr.do'
                pg = str(current_page)
                form_data = {
                    "pName": p_name,
                    "pCardNum": "",
                    "selectCourtId": "0",
                    "pCode": codes,
                    "captchaId": codes_id,
                    "searchCourtName": "全国法院（包含地方各级法院）",
                    "selectCourtArrange": "1",
                    "currentPage": pg,
                }
                meta = {
                    'codes': codes,
                    'codes_id': codes_id,
                    'pName': p_name,
                }
                yield scrapy.FormRequest(url=url, formdata=form_data, meta=meta, callback=self.page_parse)
            else:
                pass
        else:
            p_name = response.meta.get('pName')  # 获取关键词
            # print('关键词:%s无数据' % p_name)

    def parse_data(self, response):
        # ws_pc_id = response.meta('ws_pc_id')
        content_str = response.text
        content = deal_str(content_str)
        # print('详情页数据：%s'%content)
        content_dict = json.loads(content)
        # 解析详情页
        oname = content_dict.get('pname')
        cf_wsh = content_dict.get('caseCode')
        uccode = content_dict.get('partyCardNum')
        bzxr_xb = content_dict.get('sexname')
        zxfy = content_dict.get('execCourtName')
        zxwh = content_dict.get('gistId')
        lian_sj = content_dict.get('caseCreateTime')
        zx_bd = content_dict.get('execMoney')
        ws_nr_txt = content
        ws_pc_id = self.id_md5(oname, cf_wsh)
        yield {
            "ws_pc_id": ws_pc_id,
            "oname": oname,
            "bzxr_xb": bzxr_xb,
            "cf_wsh": cf_wsh,
            "uccode": uccode,
            'zxfy': zxfy,
            'zxwh': zxwh,
            'lian_sj': lian_sj,
            'zx_bd': zx_bd,
            'sj_type': 63,
            "site_id": 36699,
            'ws_nr_txt': ws_nr_txt
        }
