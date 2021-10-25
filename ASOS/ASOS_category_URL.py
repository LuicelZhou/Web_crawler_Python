'''
Created on 02/05/2019

@author: Yuyang Zhou
'''
from selenium import webdriver
import urllib, os, pymysql, time

ISOTIMEFORMAT='%Y-%m-%d %X'    #Time setup



driver = webdriver.Firefox()

driver.get('https://www.asos.com/?hrd=1')

f = open('D:/asos_category_url.txt','w')

output = driver.find_elements_by_xpath("//ul[@class='z36sLT1']//a[@class='_2Aejr0d']")   #选择@class='z36sLT1'的第一个节点
for ele in output:
    url = str(ele.get_attribute('href'))
    f.write(url + "\n")


