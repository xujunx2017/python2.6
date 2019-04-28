# coding:utf-8

import re
import json_str
from collections import OrderedDict
from pyhive import hive

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

def hive_connet(i,sql):
    list11 = []
    conn_hive = hive.Connection(host='10.0.4.142', port=10000, username='hadoop', database='default', auth='LDAP',password='DUMMY')
    cursor_hive = conn_hive.cursor()
    cursor_hive.execute(sql)
    for result in cursor_hive.fetchall():
        #print(result)
        list11.append(result[i])
    return list11

def open_json_file():
    file = open('test-data-2018-10-18.json','rb')
    content = file.read()
    jsontr = json_str.loads(content)
    return  jsontr
# print(get_target_value('bizType',jsontr,[]))

def commann(field,sql):
    for i in range(len(field)):
        open_json_file()
        table_value=get_target_value(field[i], open_json_file(), [])
        hive_value = hive_connet(i,sql)
        for j in table_value:
            if j in hive_value:
                pass
            else:
                print(table_value, '****', hive_value,'******', field[i])


if __name__ == '__main__':
    # field = ['crNo', 'idCard', 'mobile', 'applyNo', 'memberType', 'orgCount_0_6', 'orgCount_6_12', 'orgCount_12_24',
    #          'approved_0_6', 'approved_6_12', 'approved_12_24', 'rejected_0_6', 'rejected_6_12', 'rejected_12_24',
    #          'inProgress_0_6', 'inProgress_6_12', 'inProgress_12_24', 'lastRejectTime', 'loanTotal', 'uncleared',
    #          'unclearedAmount', 'overdueUncleared', 'overdueUnclearedAmount', 'normalLoanOrgCount',
    #          'overdueUnclearedMaxTime', 'overdueCleared', 'overdueClearedAmount', 'overdueMaxTime',
    #          'loanOriginationTime', 'loanOriginationAmount', 'overdueClearedAmount', 'overdueAmount', 'overdueMaxTime',
    #          'period', 'loanOriginationOrgCount', 'loanRejectedOrgCount', 'loanOriginationAmount',
    #          'overdueClearedAmount', 'overdueAmount', 'overdueOrgCount', 'overdueMaxTime', 'queryOrgCount', 'queryTime']
    field = ["crNo","idCard","mobile","applyNo","quotaValue","desc","queryTime"]
    sql = raw_input('请输入hive表sql语句：')
    commann(field,sql)


