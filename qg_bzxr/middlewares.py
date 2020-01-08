# -*- coding: utf-8 -*-


from scrapy.downloadermiddlewares.retry import RetryMiddleware
import logging
from scrapy.utils.response import response_status_message
from scrapy.utils.python import global_object_name
import json
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib import parse
from work_utils.get_code import check_code
import re
from work_utils.get_randomip import get_proxy


class CheckResponseContentMiddleware(object):  # 检查响应内容
    def process_response(self, request, response, spider):
        url = response.url
        url2 = 'searchBzxr'
        url3 = 'newdetail'
        response_status = response.status
        # print('响应码', response_status)
        if response_status != 200:
            if url2 in url:
                codes_dict = check_code()
                codes = codes_dict.get('codes')
                captcha_id = codes_dict.get('codes_id')
                request_body = unquote(request.body.decode())
                body_dict = dict(parse.parse_qsl(request_body))
                body_dict['pCardNum'] = ''
                body_dict['pCode'] = codes
                body_dict['captchaId'] = captcha_id
                request.meta['codes'] = codes
                request.meta['codes_id'] = captcha_id
                quote_body = urlencode(body_dict)
                request = request.replace(body=quote_body, meta=request.meta)
                # print('列表页修改成功')
                request.priority = 10
                return request
            else:
                codes_dict = check_code()
                codes = codes_dict.get('codes')
                captcha_id = codes_dict.get('codes_id')
                response_url = response.url
                sub_code = re.sub(r'pCode=.*?&', 'pCode={}&', response_url)
                sub_id = re.sub(r'captchaId=.*', 'captchaId={}', sub_code)
                new_url = sub_id.format(codes, captcha_id)
                # print('修改后的url：',new_url)
                request = request.replace(url=new_url)
                return request
        else:
            response_content = response.text
            if url2 in url:
                try:
                    data_list = json.loads(response_content)
                    data_dict = data_list[0]
                    return response
                except Exception as e:  # 验证码失效 更换验证码 返回请求内容
                    # print("列表页失败")
                    codes_dict = check_code()
                    codes = codes_dict.get('codes')
                    captcha_id = codes_dict.get('codes_id')
                    # print('验证码：', codes)
                    request_body = unquote(request.body.decode())
                    body_dict = dict(parse.parse_qsl(request_body))
                    body_dict['pCardNum'] = ''
                    body_dict['pCode'] = codes
                    body_dict['captchaId'] = captcha_id
                    request.meta['codes'] = codes
                    request.meta['codes_id'] = captcha_id
                    quote_body = urlencode(body_dict)
                    request = request.replace(body=quote_body, meta=request.meta)
                    # print('列表页修改成功')
                    request.priority = 10
                    return request
            else:
                response_content = response.text
                try:
                    content = json.loads(response_content)
                    if response_content == '{}':  # 验证码失效
                        # print('详情页错误')
                        codes_dict = check_code()
                        codes = codes_dict.get('codes')
                        captcha_id = codes_dict.get('codes_id')
                        response_url = response.url
                        sub_code = re.sub(r'pCode=.*?&', 'pCode={}&', response_url)
                        sub_id = re.sub(r'captchaId=.*', 'captchaId={}', sub_code)
                        new_url = sub_id.format(codes, captcha_id)
                        # print('修改后的url：',new_url)
                        request = request.replace(url=new_url)
                        return request
                    else:
                        return response
                except Exception as e:
                    codes_dict = check_code()
                    codes = codes_dict.get('codes')
                    captcha_id = codes_dict.get('codes_id')
                    response_url = response.url
                    sub_code = re.sub(r'pCode=.*?&', 'pCode={}&', response_url)
                    sub_id = re.sub(r'captchaId=.*', 'captchaId={}', sub_code)
                    new_url = sub_id.format(codes, captcha_id)
                    # print('修改后的url：',new_url)
                    request = request.replace(url=new_url)
                    return request
        return response


class MyRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats

        if retries <= retry_times:
            logging.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                          {'request': request, 'retries': retries, 'reason': reason},
                          extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logging.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                          {'request': request, 'retries': retries, 'reason': reason},
                          extra={'spider': spider})


class MyProcessException(object):
    def process_exception(self, request, exception, response):
        # print('获取异常%s' % repr(exception))
        if 'TimeoutError' in repr(exception):
            url = response.url
            url3 = 'newdetail'
            # 访问失败更换ip及验证码
            if url3 in url:
                codes_dict = check_code()
                codes = codes_dict.get('codes')
                captcha_id = codes_dict.get('codes_id')
                response_url = response.url
                sub_code = re.sub(r'pCode=.*?&', 'pCode={}&', response_url)
                sub_id = re.sub(r'captchaId=.*', 'captchaId={}', sub_code)
                new_url = sub_id.format(codes, captcha_id)
                # print('修改后的url：',new_url)
                request = request.replace(url=new_url)
            return request
        elif 'ConnectionError' in repr(exception):
            return request
        elif 'ConnectionRefusedError' in repr(exception):
            return request
        else:
            logging.error('错误：%s' % repr(exception))


class RandomCompanyProxyMiddleware(object):
    def process_request(self, request, spider):
        dict_proxy = get_proxy()
        if request.url.startswith("http://"):
            request.meta['proxy'] = dict_proxy.get("http")
            # logging.debug("请求http开头的网站，当前ip:%s" % dict_proxy.get("http")[7:])
        else:
            request.meta['proxy'] = dict_proxy.get("https")
            # logging.debug("请求https开头的网站，当前ip:%s************" % dict_proxy.get("http")[8:])
