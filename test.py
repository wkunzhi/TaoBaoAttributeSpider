# -*- coding: utf-8 -*-
# __author__ = "zok" 
# Date: 2019/3/12  Python: 3.7
import re
import pymongo

with open('re_test', 'r', encoding='utf-8') as f:
    info = f.read()
list1 = re.findall(r'"label":"(.{1,50})","required":false,', info)

label_list = sorted(set(list1), key=list1.index)  # 去重
print(label_list)
label_list = label_list[label_list.index('3:4商品图片') + 2:]
# 获取类目
catalogs = re.findall(r'当前类目：(.{1,200})</h2>', info)[0]
data = {'类目': catalogs, '属性': {}}
# 插入数据
for i in label_list:
    wo = re.findall(r'"label":"' + i + '",(.*?)]', info)[0]
    print(wo)
    data['属性'][i] = re.findall(r'"text":"(.{1,20})"}', wo)

# print(data)
# client = pymongo.MongoClient('mongodb://localhost:27017/')

# my_col = client['taobao']['goods']
# x = my_col.insert_one(data)
# if x:
#     print(catalogs)



