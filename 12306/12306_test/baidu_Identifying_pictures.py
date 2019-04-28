# -*- coding: utf-8 -*-：
#借鉴地址：https://zhuanlan.zhihu.com/p/32205732

import requests
import json
from bs4 import BeautifulSoup
import re

sission = requests.session()
headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

#上传图片
def upload_pic(img,filex):
    url = 'http://image.baidu.com/n/image?fr=form&target=pcSearchImage&needText=true'
    img.save('C:\\Users\\admin\\PycharmProjects\\untitled\\12306_test\\image\\'+filex+'.jpg')
    img_url = 'C:\\Users\\admin\\PycharmProjects\\untitled\\12306_test\\image\\'+filex+'.jpg'
    files = {
        'image':('image.jpg',open(img_url,'rb'),'image/jpeg'),
        'fr':'form',
        'target':'pcSearchImage',
        'needText':'true'
    }
    resp = sission.post(url, files=files, headers=headers)
    redirect_url = json.loads(resp.text)
    pc_search_url = redirect_url['data']['pageUrl']
    return (pc_search_url)



#获得图片结果
def get_pic_content(img,filex,index):
    li = []
    similar_url = upload_pic(img,filex).replace('pc_search', 'similar')
    #print("-----第{}张图片查询地址：{}".format(str(index+1),similar_url))
    res = sission.get(similar_url,headers =headers)
    for fromTitle in res.json()['data']:
        li.append(fromTitle['fromPageTitle'])
    # x1 = "|".join(li)
    # print(x1)
    return ("|".join(x for x in li))

if __name__ == '__main__':
    get_pic_content()



