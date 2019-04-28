# -*- coding: utf-8 -*-：
import sys
reload(sys)
sys.setdefaultencoding('utf-8') #python2转化中文
import os
import datetime
import requests
import time


headers = {
    "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/68.0.3440.106 Safari/537.36"
}

file = "C:/Users/admin/PycharmProjects/untitled/12306_test/station_name/"
if not os.path.exists(file):
    os.mkdir(file)

#站点名称和对应的编码code
def  station_name_code(reqs):
    name_code_list = {}
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9085'
    res = reqs.get(url,headers=headers,verify=False)
    #print(res.text)
    station_name_list = res.text.split('=')[1].split('@')
    #print(station_name_list)
    for each in station_name_list:
        if each !="'":
            station_name = each.split('|')[1]
            station_code = each.split('|')[2]
            name_code_list[station_name]=station_code
    return name_code_list


#校验输入查询的日期是否在预售期
def check_train_date():
    #当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    #当前时间生成时间数组
    current_time_array = time.strptime(current_time,"%Y-%m-%d")
    #时间数组变为时间戳
    current_time_stamp = time.mktime(current_time_array)
    # 火车票预售最大日期check_train_date()
    tickets_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    tickets_time_array = time.strptime(tickets_time,"%Y-%m-%d")
    #火车票最大预售期时间戳
    tickets_time__stamp  = time.mktime(tickets_time_array)
    train_date = raw_input("请输入查票日期（参照2018-12-28）：")
    time_array = time.strptime(train_date,"%Y-%m-%d")
    #查票时间戳
    train_date_stamp = time.mktime(time_array)
    #生成标准查票时间
    train_date_time = time.strftime("%Y-%m-%d",time.localtime(train_date_stamp))

    if (train_date_stamp >=current_time_stamp) and (train_date_stamp < tickets_time__stamp):
         return train_date_time
    else:
        print('查票日期不在预售时间内，请重新输入查票日期！')
        return check_train_date()



#查票接口
def query_tickets(reqs):
    from_station = raw_input("请输入起始站：")
    to_station = raw_input("请输入终点站：")
    train_date = check_train_date()
    name_code = station_name_code(reqs)
    from_station = name_code[from_station.decode('utf-8')]
    to_station = name_code[to_station.decode('utf-8')]
    #订票页查询接口
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(train_date,from_station,to_station)
    #print(url)
    res = reqs.get(url,headers = headers,verify=False)
    train_info = res.json()['data']['result']
    train_list = []
    #print(train_info)
    for item in train_info:
        split_item = item.split('|')
        item_dict = {}
        #print(split_item)
        #enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
        for index,item in enumerate(split_item,0):
            # with open(file+'train_info.txt','a+') as f:
            #     f.write(str(index)+','+item+'\n')
            print('{}:\t{}'.format(index,item))
        if split_item[11] == 'Y':  #已经开始买票
            item_dict['train_name'] = split_item[3]  # 车次名
            item_dict['depart_time'] = split_item[8]  # 出发时间
            item_dict['arrive_time'] = split_item[9]  # 到站时间
            item_dict['spend_time'] = split_item[10]  # 经历时长
            item_dict['wz'] = split_item[29]  # 无座
            item_dict['yz'] = split_item[28]  # 硬座
            item_dict['yw'] = split_item[26]  # 硬卧
            item_dict['rw'] = split_item[23]  # 软卧
            item_dict['td'] = split_item[32]  # 特等座
            item_dict['yd'] = split_item[31]  # 一等座
            item_dict['ed'] = split_item[30]  # 二等座
            item_dict['dw'] = split_item[33]  # 动卧
            train_list.append(item_dict)
        print train_list



if __name__ == '__main__':
    reqs = requests.session()
    query_tickets(reqs)
