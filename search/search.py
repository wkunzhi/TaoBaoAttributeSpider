# -*- coding: utf-8 -*-
# __author__ = "zok" 
# Date: 2019/3/1  Python: 3.7
import re
import pymysql

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

from config import *


class Search(object):
    """
    Search Class
    """
    chrome_options = webdriver.ChromeOptions()

    # 拦截端口
    chrome_options.add_argument("--proxy-server=http://127.0.0.1:8080")
    browser = webdriver.Chrome(executable_path='./utils/chromedriver', chrome_options=chrome_options)

    wait = WebDriverWait(browser, 10, 0.1)

    def start(self):
        try:
            class_type = CLASS_TYPE

            with open('path.txt', 'r', encoding='utf-8') as f:
                info_list = f.read().split(',')
                if len(info_list) == 4:
                    total = self.search(class_type, info_list[0], info_list[1], info_list[2])
                elif len(info_list) == 3:
                    total = self.search(class_type, info_list[0], info_list[1])

            # # 执行筛选
            # total = int(re.compile('(\d+)').search(total).group(1))
            # for i in range(2, total + 1):
            #     self.next_page(i)
        except Exception:
            print('fuck me!')
            self.browser.close()
        finally:
            self.browser.close()

    def search(self):
        """
        search for baby
        :param class_type: type
        :param first: class key
        :param second:  second class key
        :param thirdly:  thirdly class key
        :return:
        """
        print('search for .....')
        try:
            self.browser.get('https://upload.taobao.com/auction/publish/publish.htm')
            first_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="J_OlCascadingList"]/li[1]/div[1]/input'))
            )
            first_input.send_keys('女装/女士精品')
            first_choice = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="cc-cbox-hit"][1]'))
            )
            first_choice.click()
            second_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="J_OlCascadingList"]/li[2]/div[2]/ul'))
            )
            btn = self.browser.find_element_by_id('J_CatePubBtn').is_enabled()
            if btn:
                # 已经选到底了，采集品牌
                print('准备采集品牌')
                second_list = []
                for i in second_box.text.split('\n'):
                    if not i.encode('UTF-8').isalpha():
                        second_list.append(i)
                
            else:
                total = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
                self.get_products()
                # return total.text

                # self.go_baby_html(type_title.text)
            import time
            time.sleep(60)
        except TimeoutException:
            return self.search()

    def go_baby_html(self, type_title):
        """
        get baby class
        :return:
        """
        pass

    def back_page(self):
        """
        back page
        :return:
        """
        self.browser.back()

    def get_products(self):
        """parse html"""
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        html = self.browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('src'),  # 宝贝图片
                'price': item.find('.price').text()[2:],  # 宝贝价格
                'goods_url': item.find('.J_ClickStat').attr('href'),  # 宝贝链接
                'pay_num': item.find('.deal-cnt').text()[:-3],  # 交易人数
                'title': item.find('.title').text().replace('\n', ''),  # 宝贝标题
                'shop': item.find('.shop').text(),  # 店铺ID
                'shop_url': item.find('.J_ShopInfo').attr('href'),  # 店铺url
                'location': item.find('.location').text()  # 店铺地址
            }
            self.save_to_mysql(product)

    def save_to_mysql(self, product):
        """
        save to mysql
        :param product: html content
        :return:
        """
        image = product.get('image')
        price = product.get('price')
        goods_url = product.get('goods_url')
        pay_num = product.get('pay_num')
        title = product.get('title')
        shop = product.get('shop')
        shop_url = product.get('shop_url')
        location = product.get('location')

        # 数据库操作  【这里偷懒了，可以把这一段放在外面，不然每次插入都要链接数据库影响效率】
        db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                             password=MYSQL_PASSWORD, db=MYSQL_DB_NAME, port=MYSQL_PORT)
        # 使用cursor()方法获取操作游标
        cur = db.cursor()
        sql_insert = """insert into bg_temp_spider(select_key,image,price,goods_url,pay_num,title,shop,shop_url,location) values("%s","%s","%s","%s","%s","%s","%s","%s","%s")""" % (
            self.key, image, price, goods_url, pay_num, title, shop, shop_url, location)
        try:
            cur.execute(sql_insert)
            db.commit()
        except Exception as e:
            print('错误回滚')
            db.rollback()
        finally:
            db.close()

    def save_to_mysql_tb_baby(self, product):
        """
        save to mysql
        :param product: html content
        :return:
        """
        image = product.get('image')
        price = product.get('price')
        goods_url = product.get('goods_url')
        pay_num = product.get('pay_num')
        title = product.get('title')
        shop = product.get('shop')
        shop_url = product.get('shop_url')
        location = product.get('location')

        # 数据库操作  【这里偷懒了，可以把这一段放在外面，不然每次插入都要链接数据库影响效率】
        db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                             password=MYSQL_PASSWORD, db=MYSQL_DB_NAME, port=MYSQL_PORT)
        # 使用cursor()方法获取操作游标
        cur = db.cursor()
        sql_insert = """insert into bg_temp_spider(select_key,image,price,goods_url,pay_num,title,shop,shop_url,location) values("%s","%s","%s","%s","%s","%s","%s","%s","%s")""" % (
            self.key, image, price, goods_url, pay_num, title, shop, shop_url, location)
        try:
            cur.execute(sql_insert)
            db.commit()
        except Exception as e:
            print('错误回滚')
            db.rollback()
        finally:
            db.close()