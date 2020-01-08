import requests
import json
import time
import random
from work_utils.get_randomip import get_proxy

s = requests.session()

z_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A',
          'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
          'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
          'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
          'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
          'x', 'y', 'z']
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
}


def get_img():
    url2 = 'http://zxgk.court.gov.cn/zhixing/captcha.do?captchaId={}&random={}'
    random_num = random.random() + random.randint(1, 9) * 0.00000000000000001
    num = ''
    for i in range(0, 32):
        random_num = random.random()
        value_num = int(random_num * 61)
        num += z_list[value_num]
    url = url2.format(num, random_num)
    while True:
        try:
            proxies = get_proxy()
            # print("请求")
            response_text = s.get(url=url, headers=headers, proxies=proxies, timeout=5)
            # response_text = s.get(url=url, headers=headers)
            response_img = response_text.content
            # with open('code.jpg', 'wb') as f:
            #     f.write(response_img)
            return {'code_img': response_img, 'codes_id': num, 'random_num': random_num, 'proxies': proxies}
        except Exception as e:
            pass


# 识别验证码
def get_code():
    data_dict = get_img()
    proxies = data_dict.get('proxies')
    code_img = data_dict.get('code_img')
    codes_id = data_dict.get('codes_id')
    # result_code = requests.post(url='http://127.0.0.1:7788', data=code_img).text
    # 内网
    result_code = requests.post(url='http://192.168.1.193:18080', data=code_img).text

    codes = json.loads(result_code).get('code')
    return {'codes': codes, 'codes_id': codes_id, 'proxies': proxies}


def check_code():
    while True:
        try:
            data_dict = get_code()
            proxies = data_dict.get('proxies')
            codes = data_dict.get('codes')
            codes_id = data_dict.get('codes_id')
            url = 'http://zxgk.court.gov.cn/zhixing/searchBzxr.do'
            # key_word = str(random.randint(10, 9000000))
            key_word = '天津'
            form_data = {
                "pName": key_word,
                "pCardNum": "",
                "selectCourtId": "0",
                "pCode": codes,
                "captchaId": codes_id,
                "searchCourtName": "全国法院（包含地方各级法院）",
                "selectCourtArrange": "1",
                "currentPage": "1",
            }
            # resp = requests.post(url=url, data=form_data, headers=headers)
            resp = requests.post(url=url, data=form_data, headers=headers, proxies=proxies, timeout=10)
            # print('验证码：%s' %codes)
            # print(resp.text)
            return {'codes': codes, 'codes_id': codes_id}
        except Exception as e:
            time.sleep(1)


if __name__ == '__main__':
    num = 0
    for i in range(1, 4):
        num += 1
        data_dict = check_code()
        print(data_dict, num)
        time.sleep(1)
