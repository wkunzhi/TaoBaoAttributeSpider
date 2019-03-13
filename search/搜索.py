# -*- coding: utf-8 -*-
# __author__ = "zok" 
# Date: 2019/3/13  Python: 3.7


import time
import re
import pymongo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Search(object):
    options = webdriver.FirefoxOptions()

    # 拦截端口
    options.add_argument("--proxy-server=http://127.0.0.1:8080")
    browser = webdriver.Firefox(executable_path='./utils/geckodriver', firefox_options=options)

    wait = WebDriverWait(browser, 100, 1)

    def __init__(self):
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.my_col = client['taobao']['goods']

    def start(self):
        try:
            self.browser.get('https://upload.taobao.com/auction/publish/publish.htm')
            while True:
                self.get_data()
        except Exception:
            print('运行错误')
            self.browser.close()
        finally:
            self.browser.close()

    def get_data(self):
        try:
            input_id = self.wait.until(
                EC.presence_of_element_located(
                    (By.ID, 'button-catpath'))
            )

            if self.save_to_mongodb(self.browser.page_source):
                input_id.click()
                time.sleep(3)
        except:
            time.sleep(5 )

    def save_to_mongodb(self, info):
        # print(info)
        list1 = re.findall(r'"label":"(.{1,50})","required":false,', info)
        label_list = sorted(set(list1), key=list1.index)  # 去重
        label_list = label_list[label_list.index('3:4商品图片') + 2:]

        # 获取类目
        catalogs = re.findall(r'当前类目：(.{1,200})</h2>', info)[0]
        data = {'类目': catalogs, '属性': {}}
        # 插入数据
        for i in label_list:
            data['属性'][i] = re.findall(r'"text":"(.{1,20})"}', re.findall(r'"label":"' + i + '",(.*?)]', info)[0])
        x = self.my_col.insert_one(data)
        if x:
            print(catalogs)
            return True
        return False
