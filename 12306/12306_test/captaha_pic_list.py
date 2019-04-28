# -*- coding: utf-8 -*-：
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import json
from baidu_Identifying_pictures import get_pic_content,upload_pic
import sys
reload(sys)
sys.setdefaultencoding('utf-8') #python2转化中文

def pic_list(captaha_image):
    li = []
    #img_url = 'C:\\Users\\admin\\PycharmProjects\\untitled\\12306_test\\image\\code.jpg'
    #增强图片对比度1.3且保存
    ImageEnhance.Contrast(Image.open(captaha_image)).enhance(1.2).save(captaha_image)
    #读取图片
    imgs = Image.open(captaha_image)
    imgs.convert('RGB')
    #图像滤波处理，目的为图像识别抽取出图像特
    # BLUR：模糊滤波 MaxFilter:最大值滤波器
    imgs.filter(ImageFilter.BLUR).filter(ImageFilter.MaxFilter(21))
    imgs.convert('L')
    x_width,y_heigh = imgs.size
    #print(x_width,y_heigh)
    #得到每一张图片大小
    width = x_width/4
    heigth = y_heigh/2
    #print(width,heigth)
    for x_ in range(0,2):
        for y_ in range(0,4):
            left = y_ * width
            right = (y_+1)*width
            #print (left,right)
            #得到每张图片位置
            index = (x_*4)+y_
            #print(index)
            if x_ == 0:
                box = (left, x_ * heigth + 40, right, (x_ + 1) * heigth+15)
            else:
                box = (y_ * width, x_ * heigth+15, (y_ + 1) * width, (x_ + 1)*heigth-8)
                # print(box,"11111")
            #上传图片百度，获取识别结果
            text = get_pic_content(imgs.crop(box),str(x_)+str(y_),index)
            #print("-----第{}张图片返回结果：{}".format(str(index + 1), text))
            #print(text)
            # t = imgs.crop(box)
            # t.save(str(y_) +str(x_) + ".jpg")
            #计算坐标，由于12306官方验证码是验证正确验证码的坐标范围,我们取每个验证码中点的坐标(大约值)
            # ==================================================================================
            # 获取图片验证码位置，从左到右，从上到下，一个验证码图片高宽大约70
            # 第1排验证码坐标：       ‘35,35’， ‘105,35’， ‘175,35’， ‘245,35’
            # 第1排验证码坐标替换标示：   0         1          2          3
            # 第2排验证码坐标：        ‘35,105’，‘105,105’，‘175,105’，‘245,105’
            # 第2排验证码坐标替换标示：   4         5          6          7
            # ==================================================================================
            answer = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']
            #将坐标保存
            #print(text)
            li.append({answer[index]:text})
            # print("第{}张图片识别结果：{}".format(str(index+1),text))
    return li


if __name__=='__main__':
    pic_list()