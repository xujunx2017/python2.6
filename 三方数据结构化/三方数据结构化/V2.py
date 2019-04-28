# coding:utf-8
##远程服务器#####
import re
import json
from collections import OrderedDict
from pyhive import hive
import ConfigParser
import jsonpath
import os
import time
import sys


#get_target_value和_get_value解析json
def get_target_value(key, dic, tmp_list):
    """
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():

        tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    else:
        for value in dic.values():  # 传入数据不符合则对其value值进行遍历
            if isinstance(value, dict):
                get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
            elif isinstance(value, (list, tuple)):
                _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list

def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)  # 传入数据的value值是列表或者元组，则调用自身

#连接hive
def hive_connet(i,table_name):
    list11 = []
    conn_hive = hive.Connection(host='10.0.4.142', port=10000, username='hadoop', database='default', auth='LDAP',password='DUMMY')
    cursor_hive = conn_hive.cursor()
    sql = 'SELECT * FROM provider_api_db.%s LIMIT 100000'%(table_name)
    cursor_hive.execute(sql)
    for result in cursor_hive.fetchall():
        #print(result)
        list11.append(result[i])
    return list11

#读取json
def open_json_file():
    file = open('test3.json','rb')
    content = file.read()
    jsontr = json.loads(content)
    return (jsontr)

#接口和对应的json统一dict内
def method():
    method_key = []
    jsonstr = {}
    for i in range(len(open_json_file())):
        #print(open_json_file()[i])
        #jsonpath获取接口
        method_vaule = jsonpath.jsonpath(open_json_file()[i],"$..method")
        method_vaule1 = method_vaule[0].split('.')
        #按照a_b格式组装
        method_name = method_vaule1[0]+'_'+method_vaule1[1]
        #接口名和字符串都放到list
        method_key.append(method_name)
        method_key.append(open_json_file()[i])
    #list转化为dict
    for a in range(0,len(method_key),2):
        jsonstr[method_key[a]] =method_key[a+1]
    return jsonstr

#启动脚本前判断log文件是否存在
def exists_file(file,dirname):
    if os.path.exists(file):
        os.remove(file)
        print('.............................................删除脚本{},倒计时开始中.............................................\n'.format(file))
        time.sleep(3)
        commann(file, dirname)
    else:
        commann(file, dirname)

def commann(file,dirname):
    print("\033[1;33;44m..............................................脚本开始运行:staring.............................................\033[0m")
    with open(file, 'a+') as f:
        f.write("..............................................脚本开始运行:staring.............................................\n")
    for key,value in method().items():
        #判断ini文件是否存在
        if os.path.exists('{}/{}.ini'.format(dirname,key)):
            #print(key)
            conf = ConfigParser.ConfigParser()
            conf.read('{}/{}.ini'.format(dirname,key))
            # 显示颜色格式：\033[显示方式;字体色;背景色m......[\033[0m]
            print("\033[1;33;44m.............................................打开文件{}.ini.............................................\033[0m".format(key))
            with open(file, 'a+') as f:
                f.write(".............................................打开文件{}.ini.............................................\n".format(key))
            #读取配置文件
            table_list = conf.get("table_list", "table_list").strip(',').split(',')
            for table_name in table_list:
                print("---------------------------------------------正在校验{}表字段---------------------------------------------".format(table_name))
                with open(file, 'a+') as f:
                    f.write("---------------------------------------------正在校验{}表字段---------------------------------------------\n".format(table_name))
                field_name = conf.get('fields', table_name).split(',')
                root = conf.get(table_name, "root")
                optionalRoots_request = conf.get(table_name, "a")
                optionalRoots_response = conf.get(table_name, "b")
                # print(field_name)
                # print(root)
                # print(optionalRoots_request)
                # print(optionalRoots_response)
                for i in range(len(field_name)):
                    # print(i,field_name[i])
                    # 根据配置文件提供的取值路径解析json获取表字段对应的值
                    root_value = jsonpath.jsonpath(value, "$..{}..{}".format(root, field_name[i]))
                    optionalRoots_response_value = jsonpath.jsonpath(value, "$..{}..{}".format(optionalRoots_response, field_name[i]))
                    optionalRoots_request_value = jsonpath.jsonpath(value, "$..{}..{}".format(optionalRoots_request, field_name[i]))
                    #hive_value = hive(table_name, i)
                    # print(root_value)
                    # 获取hive表的所有值
                    hive_value = hive_connet(i, table_name)
                    # 通过root_value，optionalRoots_request_value，optionalRoots_response_value取值路径拿到对应字段的值
                    if root_value:
                        if len(root_value) >= 2:
                            for a in range(len(root_value)):
                                if root_value[a] in hive_value:
                                    # reload(root_value[a])
                                    print("{}字段在json内属于多值数组，测试通过".format(field_name[i]))
                                    with open(file, 'a+') as f:
                                        f.write("{}字段在json内属于多值数组，测试通过\n".format(field_name[i]))
                                elif field_name[i] == 'idCard' or field_name[i] == 'mobile' or field_name[
                                    i] == 'phone_no':
                                    print('%s字段为加密字段不用效验' % field_name[i])
                                    with open(file, 'a+') as f:
                                        f.write('%s字段为加密字段不用效验\n' % field_name[i])
                                    break
                                else:
                                    print(field_name[i], root_value, hive_value)
                                    with open(file, 'a+') as f:
                                        f.write("{} 字段在json中的值为{}，在hive数据库的值为{}\n".format(field_name[i],root_value,hive_value))

                        else:
                            for j in root_value:
                                # 判断字段对应的json和hive表值是否一致
                                if j in hive_value:
                                    print("%s字段效验通过" % field_name[i])
                                    with open(file, 'a+') as f:
                                        f.write("%s字段效验通过\n" % field_name[i])
                                elif field_name[i] == 'idCard' or field_name[i] == 'mobile' or field_name[
                                    i] == 'phone_no':
                                    print('%s字段为加密字段不用效验' % field_name[i])
                                    with open(file, 'a+') as f:
                                        f.write('%s字段为加密字段不用效验\n' % field_name[i])
                                    break
                                else:
                                    print(field_name[i], root_value, hive_value)
                                    with open(file, 'a+') as f:
                                        f.write("{} 字段在json中的值为{}，在hive数据库的值为{}\n".format(field_name[i],root_value,hive_value))
                        #print(len(root_value),field_name[i])

                    elif  field_name[i] == 'idCard' or field_name[i] == 'mobile' or field_name[i] == 'phone_no':
                        print('%s字段为加密字段不用效验' % field_name[i])
                        with open(file, 'a+') as f:
                            f.write('%s字段为加密字段不用效验\n' % field_name[i])

                    # elif field_name[i] == 'queryTime':
                    #     # 格式化时间戳为本地的时间,optionalRoots_request_value[0]毫秒转换为秒
                    #     time1 = time.localtime(optionalRoots_request_value[0] / 1000)
                    #     # time strftime() 函数接收以时间元组，并返回以可读字符串表示的当地时间
                    #     queryTime = time.strftime('%Y-%m-%d %H:%M:%S', time1)
                    #     if queryTime in hive_value[0].encode('utf-8'):
                    #         print("%s字段效验通过" % field_name[i])
                    #         with open(file, 'a+') as f:
                    #             f.write("%s字段效验通过\n" % field_name[i])
                    #     else:
                    #         print(field_name[i], queryTime, hive_value[0].encode('utf-8'))
                    #         with open(file, 'a+') as f:
                    #             f.write("{} 字段在json中的值为{}，在hive数据库的值为{}\n".format(field_name[i],queryTime,hive_value[0].encode('utf-8')))
                    elif optionalRoots_request_value:
                        for j in optionalRoots_request_value:
                            # 判断字段对应的json和hive表值是否一致
                            if j in hive_value:
                                print("%s字段效验通过" % field_name[i])
                                with open(file, 'a+') as f:
                                    f.write("%s字段效验通过\n" % field_name[i])
                            else:
                                print(field_name[i], optionalRoots_request_value, hive_value)
                                with open(file, 'a+') as f:
                                    f.write("{} 字段在json中的值为{}，在hive数据库的值为{}\n".format(field_name[i], optionalRoots_request_value,hive_value))
                    elif optionalRoots_response_value:
                        for j in optionalRoots_response_value:
                            # 判断字段对应的json和hive表值是否一致
                            if j in hive_value:
                                print("%ss字段效验通过" % field_name[i])
                                with open(file, 'a+') as f:
                                    f.write("%ss字段效验通过\n" % field_name[i])
                            else:
                                print(field_name[i], optionalRoots_response_value, hive_value)
                                with open(file, 'a+') as f:
                                    f.write("{} 字段在json中的值为{}，在hive数据库的值为{}\n".format(field_name[i], optionalRoots_response_value,hive_value))

                    # 其他字段为空则默认通过
                    else:
                        if "None" in str(hive_value):
                            print("{} 字段测试通过,该值为空".format(field_name[i]))
                            with open(file, 'a+') as f:
                                f.write("{} 字段测试通过,该值为空\n".format(field_name[i]))
                        else:
                            print(field_name[i], "None", hive_value)
                            with open(file, 'a+') as f:
                                f.write("{} 字段在hive数据库的值为{}\n".format(field_name[i],hive_value))

            print("\n")
            with open(file, 'a+') as f:
                f.write("\n")
        else:
            print("..............................................{}.ini文件不存在，请检查..............................................".format(key))
            with open(file, 'a+') as f:
                f.write("..............................................{}.ini文件不存在，请检查..............................................\n".format(key))


if __name__ == '__main__':
    # field = ['crNo', 'idCard', 'mobile', 'applyNo', 'memberType', 'orgCount_0_6', 'orgCount_6_12', 'orgCount_12_24',
    #          'approved_0_6', 'approved_6_12', 'approved_12_24', 'rejected_0_6', 'rejected_6_12', 'rejected_12_24',
    #          'inProgress_0_6', 'inProgress_6_12', 'inProgress_12_24', 'lastRejectTime', 'loanTotal', 'uncleared',
    #          'unclearedAmount', 'overdueUncleared', 'overdueUnclearedAmount', 'normalLoanOrgCount',
    #          'overdueUnclearedMaxTime', 'overdueCleared', 'overdueClearedAmount', 'overdueMaxTime',
    #          'loanOriginationTime', 'loanOriginationAmount', 'overdueClearedAmount', 'overdueAmount', 'overdueMaxTime',
    #          'period', 'loanOriginationOrgCount', 'loanRejectedOrgCount', 'loanOriginationAmount',
    #          'overdueClearedAmount', 'overdueAmount', 'overdueOrgCount', 'overdueMaxTime', 'queryOrgCount', 'queryTime']
    # field = ["crNo","idCard","mobile","applyNo","quotaValue","desc","queryTime"]
    # #sql = raw_input('请输入hive表sql语句：')
    # table_name='third_bee_ar_idcard'
    # commann(field,table_name)
    file = 'third_out.log'
    exists_file(file,'/home/appuser/xujun/三方数据结构化/三期')


