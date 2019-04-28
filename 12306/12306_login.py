#coding = utf-8
import requests

import lxml
def login():
    #验证码获取地址
    #"https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1544519246778&callback=jQuery19107461869860813457_1544519200493&_=1544519200496"
    image_url ="https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&1544519246778"
    #验证码校验接口
    #"https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery19107461869860813457_1544519200493&answer=125%2C112%2C40%2C117&rand=sjrand&login_site=E&_=1544519200495"
    url_check ="https://kyfw.12306.cn/passport/captcha/captcha-check"
    #登陆接口
    url_login = "https://kyfw.12306.cn/passport/web/login"
    headers = {
         "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
     }
    #步骤一获取验证码
    response = requests.get(image_url,headers =headers)
    code_img = response.content
    #print(result_message)
    with open("code.jpg","wb") as file:
        file.write(code_img)
    answer = str(input("请输入验证码位置："))
    #验证码接口校验需要三个参数：login_site，rand，answer
    data_check = {
        'login_site':'E',
        'rand':'sjrand',
        'answer': answer
    }

    #步骤二：校验验证码
    response = requests.post(url_check,data = data_check)
    print(response.text)

    #登陆网站
    #result_code  5验证码校验失败，7验证码过期，4校验成功1
    #格式：{'result_message': '验证码校验失败,信息为空', 'result_code': '8'}
    if response.json()["result_code"]=="4":
        username = str(input("请输入12306账号："))
        password = str(input("请输入12306密码："))
        data_login ={
            "username":username,
            "password":password,
            "appid":"otn"
        }
        response = requests.post(url_login,data = data_login)
        print(response.text)

login()

