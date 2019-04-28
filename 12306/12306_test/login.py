# -*- coding: utf-8 -*-：
import json
import threading
from threading import Thread
import urllib3
import requests
from PIL import Image
import matplotlib.pyplot as plt
from baidu_ocr import  get_img_result
import os
from captaha_pic_list import pic_list
import time

headers = {
    "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
}


#获取验证码图片
def get_img(reqs,captaha_image):
    image_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&1544519246778"
    response = reqs.get(url=image_url,headers = headers,verify = False)
    if response.status_code == 200:
        # 验证码保存到本地
        with open(captaha_image, "wb") as f:
            f.write(response.content)
            print('图片下载成功......')
            return True
    else:
        print('图片下载失败，正在重试......')
        get_img(reqs,captaha_image)


#调用baidu-ocr获取标题内容
def get_title_content(count,captaha_image,title_img):
    #标题内容
    title = []
    get_title_pic(captaha_image,title_img)
    #由于12306存在多标题，如本子，订书机这种，所以需要2个位置的标题内容都识别
    #get_title_pic(captaha_image, title_img)
    try:
        res = get_img_result(title_img)
        #print(res,"res....................................")
            #print("OCR文字识别结果：{}".format(res['words_result'][0]))
        if res['words_result'] !=0:
            title.append(res['words_result'][0]['words'])
            print("识别结果：{}".format(res['words_result'][0]['words']))
    except Exception:
        count+=1
        if count >= 2:
            print('调用OCR识别异常超过3次，请检查OCR识别接口......')
        else:
            get_title_content(count,captaha_image,title_img)
    #print(res['words_result'][0]['words'])
    return title




#获取验证码标题图片
def get_title_pic(captaha_image,title_img):
    #如本子，订书机，1，取本子位置的截图 2，取订书机位置的截图
    # index = 1
    # if index ==1:
    #     # 图片文字位置
    #     box = (116, 0, 175, 30)
    # else:
    #     box = (173,0,238,30)
    image = Image.open(captaha_image)
    box = (116, 0, 175, 30)
    #crop根据box坐标位置裁剪
    t = image.crop(box)
    t.save(title_img)


#删除文件夹或子文件夹下的所有文件
def remove_file(dirpath):
    #dirpath = 'C:\\Users\\admin\\PycharmProjects\\untitled\\12306_test\\image'
    #遍历显示dirpath下所有文件
    for i in os.listdir(dirpath):
        #组装取文件路径
        path = os.path.join(dirpath,i)
        #判断是否是文件
        if os.path.isfile(path):
            os.remove(path)
            print('{}文件删除成功'.format(path))
        else:
            remove_file(path)


def login_get_data(reqs,captaha_image,title_img):
    point = []
    count =0
    print("启动脚本前清除历史文件......,请等待5s")
    for i in range(5,0,-1):
        print(str(i)+'s')
    # print('\n')
    dirpath = 'C:\\Users\\admin\\PycharmProjects\\untitled\\12306_test\\image'
    remove_file(dirpath)
    print('开始执行脚本......')
    get_img(reqs, captaha_image)
    print("开始调用百度OCR进行文字识别......")
    result = get_title_content(count,captaha_image,title_img)
    #print('OCR文字识别结果:{}'.format(result))
    #获取验证码图片内8张图片的识别结果
    lists = pic_list(captaha_image)
    print("8张图片识别后，返回结果：{}".format(lists))
    #print(lists)
    print("开始进行内容比对......")
    # 获取8张图片对应的坐标和图片识别结果
    for li in lists:
        #print(li)
        # 获取到验证码图片的标题
        for title_text in result:
            #print(title_text)
            #对标题进行分割循环比对
            for tx in title_text:
            #po:验证码8张图片对应的坐标点，value就是图片通过上传百度后返回的识别结果
                for po,value in li.items():
                    #print(po)
                    #print(value)
                    #判断验证码图片的标题是否在图片识别结果内
                    if tx in value:
                        #print(po)
                        #由于每张图片的识别结果很多，所以判断当前坐标点是否存在
                        if po not in point:
                            print("验证码标题：{}，图片识别结果：{}，识别到一个坐标点：{}......".format(tx,value,po))
                            point.append(po)
                    else:
                        print('验证码标题:{},与图片识别结果：{}不匹配.'.format(tx,value))
    return point

#验证码校验
def check_captcha(reqs,point):
    # 校验接口
    url_check = "https://kyfw.12306.cn/passport/captcha/captcha-check"
    data_check = {
        'login_site': 'E',
        'rand': 'sjrand',
        'answer': ','.join(point)
    }
    res = reqs.post(url_check,data = data_check,headers = headers)
    if res.status_code !=200:
        return False
    jsonstr = json.loads(res.text)
    print("验证码接口返回结果{}：".format(jsonstr))
    code = jsonstr['result_code']
    # 取出验证结果，4：成功  5：验证失败  7：过期
    if str(code) == '4':
        return True
    else:
        return False


#登陆
def login_12306(reqs,captaha_image,title_img):
    point = login_get_data(reqs,captaha_image,title_img)
    if len(point) != 0:
        print("验证码校验成功，坐标点为：{}，进行尝试登陆......").format(point)
        check=check_captcha(reqs,point)
        if check is True:
            print("验证码校验成功......")
            # 登陆接口
            url_login = "https://kyfw.12306.cn/passport/web/login"
            data_login = {
                        "username":'x234115233',
                        "password":'5078346xjj',
                        "appid":"otn"
                    }
            result = reqs.post(url_login, data=data_login,headers = headers)
            print("登陆成功，返回结果......")
            print(result.text)
            if result.json()['result_message'] == '登录成功':
                uamtk = result.json()['uamtk']
                return True
            else:
                return False
        else:
            print("验证码校验失败，重新获取验证码重新校验......")
            print('\n')
            print('休眠10s后，重新尝试登陆')
            time.sleep(10)
            login_12306(reqs, captaha_image, title_img)
    else:
        print("识别图片内容失败，正在重试......")
        # time.sleep(5)
        # login( reqs, captaha_image, title_img)


def auth_uamtk(reqs):
    """
        根据登录返回的umatk,得到newapptk
        :return:
    """
    url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
    data = {
        'appid':'otn'
    }
    res = reqs.post(url,data=data,headers = headers)
    newapptk = res.json()['newapptk']
    return newapptk


#检查客户端是否登录
def otn_uamauthclient(reqs):
    """
        检查客户端是否登录
        :param tk:
        :return:
    """
    url = 'https://kyfw.12306.cn/otn/uamauthclient'
    tk = auth_uamtk(reqs)
    data = {
        'tk': tk
    }
    res = reqs.post(url,data=data,headers=headers)
    if res.json()['result_message'] == '验证通过':
        print(res.text)
    else:
        print("客户端登录失败")
        print(res.text)






if __name__ == '__main__':
    # 创建网络请求session实现登陆,非同一个session验证码会返回8，信息为空
    reqs = requests.session()
    captaha_image = '../12306_test/image/code.jpg'
    title_img = '../12306_test/image/title.jpg'
    login = login_12306(reqs, captaha_image, title_img)
    if login is True:
        otn_uamauthclient(reqs)
    else:
        print('登录失败......')


