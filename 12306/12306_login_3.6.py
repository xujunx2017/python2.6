# -*- coding: utf-8 -*-：
import json
import threading
from threading import Thread
import urllib3
import requests
from PIL import Image
import matplotlib.pyplot as plt
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



#获取验证码图片
def get_img(res):
    headers = {
                 "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
             }
    image_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&1544519246778"
    response = res.get(url=image_url,headers = headers,verify = False)
    # 验证码保存到本地
    with open("code.jpg", "wb") as f:
        f.write(response.content)
    img = Image.open('code.jpg')
    plt.figure("验证码")
    plt.imshow(img)
    #打开交互模式
    plt.ion()
    plt.pause(10)
    plt.close()
    #==================================================================================
    #获取图片验证码位置，从左到右，从上到下，一个验证码图片高宽大约70
    #第1排验证码坐标：       ‘35,35’， ‘105,35’， ‘175,35’， ‘245,35’
    #第1排验证码坐标替换标示：   0         1          2          3
    #第2排验证码坐标：        ‘35,105’，‘105,105’，‘175,105’，‘245,105’
    #第2排验证码坐标替换标示：   4         5          6          7
    # ==================================================================================
    captcha_position = input("请输入验证码位置，以，隔开：")
    return captcha_position

#校验验证码正确性
def check_captcha(res):
    headers = {
        "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    url_check = "https://kyfw.12306.cn/passport/captcha/captcha-check"
    answer = ['35,35','105,35','175,35','245,35','35,105','105,105','175,105','245,105']
    captcha_list1 = get_img(res).split(',')
    captcha_list = []
    for i in captcha_list1:
        captcha_list.append(answer[int(i)])
    #join方法让验证码去掉’‘，以，隔开显示
    captcha_str = ','.join(captcha_list)
    # 验证码接口校验需要三个参数：login_site，rand，answer
    data_check = {
            'login_site':'E',
            'rand':'sjrand',
            'answer': captcha_str
        }
    # print(data_check)
    # #发送验证
    response = res.post(url = url_check,data = data_check,headers = headers,verify = False)
    if response.status_code !=200:
        return False
    jsonstr = json.loads(response.text)
    code = jsonstr['result_code']
    # 取出验证结果，4：成功  5：验证失败  7：过期
    if str(code) == '4':
        return True
    else:
        return False

#登陆
def login(res):
    check = check_captcha(res)
    if check is True:
        print("验证码校验成功......")
        url_login = "https://kyfw.12306.cn/passport/web/login"
    else:
        print("验证码校验失败,正在重新尝试......")
        login(res)

if __name__ == '__main__':
    # 创建网络请求session实现登陆,非同一个session验证码会返回8，信息为空
    res = requests.session()
    login(res)


# def login():
#     #验证码获取地址
#     #"https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1544519246778&callback=jQuery19107461869860813457_1544519200493&_=1544519200496"
#     image_url ="https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&1544519246778"
#     #验证码校验接口
#     #"https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery19107461869860813457_1544519200493&answer=125%2C112%2C40%2C117&rand=sjrand&login_site=E&_=1544519200495"
#     url_check ="https://kyfw.12306.cn/passport/captcha/captcha-check"
#     #登陆接口
#     url_login = "https://kyfw.12306.cn/passport/web/login"
#     headers = {
#          "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
#      }
#     #步骤一获取验证码
#     response = requests.get(image_url,headers =headers)
#     code_img = response.content
#     #print(result_message)
#     answer = str(input("请输入验证码位置："))
#     #验证码接口校验需要三个参数：login_site，rand，answer
#     data_check = {
#         'login_site':'E',
#         'rand':'sjrand',
#         'answer': answer
#     }
#
#     #步骤二：校验验证码
#     response = requests.post(url_check,data = data_check)
#     print(response.text)
#
#     #登陆网站
#     #result_code  5验证码校验失败，7验证码过期，4校验成功
#     #格式：{'result_message': '验证码校验失败,信息为空', 'result_code': '8'}
#     if response.json()["result_code"]=="4":
#         username = str(input("请输入12306账号："))
#         password = str(input("请输入12306密码："))
#         data_login ={
#             "username":username,
#             "password":password,
#             "appid":"otn"
#         }
#         response = requests.post(url_login,data = data_login)
#         print(response.text)
#
# login()

