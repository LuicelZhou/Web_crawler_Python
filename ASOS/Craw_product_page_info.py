'''
Created on 02/05/2019
Crawl product page information.

@author: Yuyang Zhou
'''

# -*- coding: utf-8 -*-
from selenium import webdriver
import urllib, os, pymysql, time,re
from selenium.common.exceptions import NoSuchElementException

ISOTIMEFORMAT='%Y-%m-%d %X'    #Time setup

#f = open("D:/product_list.txt",'w')

def saveImgs(driver, img_path, img_url_list):
    img_num = 0
    if not os.path.exists(img_path):  ###判断文件是否存在，返回布尔值
        os.makedirs(img_path)

    while img_num < len(img_url_list):
        image_url = img_url_list[img_num]
        save_path = img_path + str(img_num) + '.jpg'
        urllib.request.urlretrieve(image_url, save_path)
        img_num = img_num + 1
    return img_num

def check_exists_by_xpath(driver, xpath):   #检查p是否存在
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def craw_product_contents(product_url):
    product_info_list = []
#     driver = webdriver.PhantomJS()
#     driver = webdriver.Firefox()
    driver.get(product_url)

    time.sleep(1)
    url_product_id = re.findall(r'[0-9]{7}',product_url)[0] #正则表达式——找到所有匹配七位0-9的数字 选择第一个
    product_info_list.append(url_product_id)
    
    #show more（假如还需要点击“show more”——全页面下方信息）
    show_more = driver.find_element_by_xpath("//a[@class='show']")
    if show_more.is_enabled():
        show_more.click()

    #breadcrumb
    breadcrumb = ''
    breadcrumb_eles = driver.find_elements_by_xpath("//div[@id='breadcrumb']/ul/li")    #图片上方那一行信息的地址（即想得到的详细分类信息）
    for breadcrumb_ele in breadcrumb_eles:
        breadcrumb = breadcrumb + breadcrumb_ele.text + '/'
    breadcrumb = breadcrumb.strip('/')
    product_info_list.append(breadcrumb)
    
    #product URL
    product_info_list.append(product_url)
    
    # URL state is 1 假如网页还存在（没刷新）
    product_url_stat = 1
    product_info_list.append(product_url_stat)
    
    #product code   产品编号
    product_code =''
    product_code = driver.find_element_by_xpath("//div[@class='product-code']/span").text
    product_info_list.append(product_code)

    #product website
    product_website = 'http://www.asos.com/'
    product_info_list.append(product_website)

    #product gender
    gender = 0
    if 'Men' in breadcrumb:
        gender = 1
    else:
        gender = 0
    product_info_list.append(gender)

    #product_brand
    product_brand = 'ASOS'
    product_info_list.append(product_brand)

    #product_craw_time 爬取产品时间
    product_craw_time = time.strftime(ISOTIMEFORMAT,time.localtime(time.time())) #获取当前时区时间格式 2016-08-02 21:46:38
    product_info_list.append(product_craw_time)
    
    #product title
    product_title = ''
    product_title = driver.find_element_by_xpath("//div[@class='product-hero']/h1").text
    product_info_list.append(product_title)

    '''#product delivery???
    product_delivery = ''
    product_delivery = driver.find_element_by_xpath("//a[@class='product-delivery']").text
    product_info_list.append(product_delivery)'''

    #product price
    product_price = 0
    if check_exists_by_xpath(driver,"//span[@class='current-price']"):
        product_price = driver.find_element_by_xpath("//span[@class='current-price']").text
        product_info_list.append(product_price)

    else:
        product_price = driver.find_element_by_xpath( "//span[@class='current-price product-price-discounted']").text
        product_info_list.append(product_price)


    #product description    
    product_description = ''
    product_description = driver.find_element_by_xpath("//div[@class='product-description']/span").text.strip()

    #product about product material
    product_material = ''
    product_material = driver.find_element_by_xpath("//div[@class='about-me']/span").text.strip()
    product_description = product_material + ';;' + product_description
    product_info_list.append(product_description.strip(';;'))


    #product select size can be null
    size = ''
    product_size = driver.find_element_by_xpath("//div[@class='colour-size-select']").find_elements_by_xpath("//select[@data-id='sizeSelect']/option")
    for ele in product_size:
        if 'Not' not in ele.text and 'Please' not in ele.text:
            size = size + ele.text + ';;'
    size = size.strip(';;')
    product_info_list.append(size)

    #product care INFO
    product_care = ''
    product_care = driver.find_element_by_xpath("//div[@class='care-info']/span").text.strip()
    product_info_list.append(product_care)

    #product colour
    product_colour = ''
    product_colour = driver.find_element_by_xpath("//span[@class='product-colour']").text
    product_info_list.append(product_colour)
    
    #product IMGs
    img_url_list = []
    ele_imgs = driver.find_elements_by_xpath("//img[@class='gallery-image']")
    for ele in ele_imgs:
        img_url_list.append(ele.get_attribute("src"))
    img_url_list = list(set(img_url_list))
    
    img_path = 'Unclassified'
    if len(breadcrumb) > 0:
        img_path = '/'.join(breadcrumb.split('/')[0:-1])

    img_number = saveImgs(driver, ROOTPATH + breadcrumb + '/' + str(url_product_id) + "/", img_url_list)
    product_info_list.append(img_number)

    # threre are at most 3 right-arrow button, click it if it is clickable
    right_arrows = driver.find_elements_by_xpath("//a[@class='arrow right-arrow active']")
    if len(right_arrows) == 2:
        right_arrows[1].click()
        right_arrows[1].click()
        right_arrows[1].click()
        right_arrows[1].click()
    if len(right_arrows) == 3:
        right_arrows[1].click()
        right_arrows[1].click()
        right_arrows[1].click()
        right_arrows[1].click()


    #buy the look（相似推荐）
    buy_the_look_list = ''
    look_list = []
    buy_the_look_componet = driver.find_element_by_xpath("//div[@class='component buy-the-look']")
    buy_the_look = buy_the_look_componet.find_elements_by_xpath("//div[@class='btl-product-details']/a")
    for ele in buy_the_look:
        if ele.get_attribute('href') is not None and 'complete' in ele.get_attribute('href'):
            if ele.get_attribute('href') not in look_list:
                look_list.append(ele.get_attribute('href'))
    buy_the_look_list = ';;'.join(look_list)
    product_info_list.append(buy_the_look_list)


    #you may also like（搭配）
    you_may_also_like_list = ''
    like_list = []
    you_may_also_like_component = driver.find_element_by_xpath("//div[@class='component might-like']")
    you_may_also_like = you_may_also_like_component.find_elements_by_xpath("//ul[@class='slide-panel']/li/a")

    for ele in you_may_also_like:
        if ele.get_attribute('href') is not None and 'recommend' in ele.get_attribute('href'):
            if ele.get_attribute('href') not in like_list:
                like_list.append(ele.get_attribute('href'))
    you_may_also_like_list = ';;'.join(like_list)
    product_info_list.append(you_may_also_like_list)
    #f.write(str(product_info_list)+'\n')

#     product_details_data = (url_product_id, breadcrumb, product_url, product_url_stat, product_code, product_website, 
#                             gender, product_brand, product_craw_time, 
#                             product_title, product_delivery, product_price, product_description, size,
#                             product_care, product_colour, img_number, buy_the_look_list, you_may_also_like_list)
#     driver.quit()
    return product_info_list

'''def store_in_database(product_data):
    #start of database updating
    sql_update_content = """
    INSERT INTO testdb.product(
    product_breadcrumbs,
    product_url,
    product_url_stat,
    product_sku,
    product_website,
    product_gender,
    product_brand,
    product_craw_time,
    product_title,
    product_estimated_delivery_time,
    product_price,
    product_desc,
    product_stock_hint,
    product_size_detail1,
    product_size_detail2,
    product_img_number,
    product_similar,
    product_match)
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(sql_update_content, product_data)
    db.commit()#需要这一句才能保存到数据库中'''


if __name__ == '__main__':  #主函数
    product_URLs = open("D:/product_url.txt")
    ROOTPATH = "D:/workspace/ASOS/"
    
    #db = pymysql.connect("localhost","root","123456","testdb", charset="utf8")      #数据库连接
    #cursor = db.cursor()
    driver = webdriver.Firefox()
    
    for product_url in product_URLs:
        product_data = craw_product_contents(product_url)
        print(product_data)
#         try:
#             product_data = craw_product_contents(driver)
#             print(product_data)
#     #         store_in_database(product_data)
#         except:
#             print("crawl page content error")
    
    product_URLs.close()
    #db.close()  #数据库关闭