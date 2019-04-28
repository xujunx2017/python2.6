# -*- coding: utf-8 -*-：
from aip import AipOcr

'''
    APP_ID,API_key,SECRET_KEY 百度注册应用获取
    地址：http://ai.baidu.com/docs#/OCR-Python-SDK/top
'''
APP_ID = '15155898'
API_key = 'VeB15daNuo3yPALM7V0Kq8KV'
SECRET_KEY = 'IoFWGyzOpL4CIFzqvUv6TvMVBNFeui5x'


#实例
AipOcr =AipOcr(APP_ID,API_key,SECRET_KEY)

#参数
options = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG'
}

#获取图片数据
def get_file_content(filepath):
    with open(filepath,'rb') as fp:
        return fp.read()

#调用通用文字识别（高精度版）获取图片内容
def get_img_result(image_url):
    img = get_file_content(image_url)
    return AipOcr.basicAccurate(img,options)


if __name__=='__main__':
    result = get_img_result('code1.jpg')
    print(result['words_result'][0]['words'])


