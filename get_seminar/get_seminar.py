# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 22:37:27 2019

@author: 王志
"""

#为新媒体而做，爬取指定网页的
import supports_wangz as wangz
import logging
import os
import configparser
import base64
import webbrowser
from datetime import datetime
import time

#先定义日志操作
logger=logging.getLogger("logger")
logger.setLevel(logging.INFO)
#定义处理器，用于文件输出和控制台输出
handler1=logging.StreamHandler()
handler2=logging.FileHandler(filename="logging_user",encoding='utf-8')
handler1.setLevel(logging.DEBUG)
handler2.setLevel(logging.ERROR)
formatter=logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)
logger.addHandler(handler1)
logger.addHandler(handler2)




#定义几个需要的url 
HSBC_seminar="https://www.phbs.pku.edu.cn//about//Allnews//seminar//index.html"##汇丰商学院的网站
law_school_url="http://stl.pku.edu.cn//zh-hans//news//%E6%96%B0%E9%97%BB%E4%B8%AD%E5%BF%83//%E9%80%9A%E7%9F%A5%E5%85%AC%E5%91%8A//"##国际法学院的网站
TSINGHUA_url="http://www.sigs.tsinghua.edu.cn//xsdt//index.jhtml"##清华深研院的网站
HIT_url="http://www.hitsz.edu.cn//article//id-78.html"#哈工大网站
utsz_lecture_url="https://lib.utsz.edu.cn/lecture/schedule.html?locale=zh_CN"#大学城的讲座
test_url="http://stl.pku.edu.cn/zh-hans/%e6%96%b0%e9%97%bb%e4%b8%ad%e5%bf%83/%e3%80%90%e5%88%86%e4%ba%ab%e4%bc%9a%e9%a2%84%e5%91%8a%e3%80%916%e6%9c%8820%e6%97%a5%ef%bc%88%e5%91%a8%e5%9b%9b%ef%bc%89%ef%bc%9a2019%e5%b1%8a%e6%af%95%e4%b8%9a%e7%94%9f%e5%ae%9e%e4%b9%a0%e5%b0%b1/"


#版权相关信息
copy_right='''All rights reserved from bailin 2019.9.8 from PKU@SAM
update data:2019.10.27
version number :1.0'''



##定义几个路径


#文件夹不可存在的符号
error_key=['\\',r'/',r':','*',"?",r'"',r"<",r">",r"|",r"."]
if __name__=="__main__":
    print("{0:-^30}".format(copy_right))
    print("-----------------------------------------------------")
    print("\n")  
    text_id=0   
    #首先读取目录下面的配置文件
    cf=configparser.ConfigParser()
    try:        
        cf.read("config.ini",encoding='utf-8')
        user_name=cf.get("user","name")
        passwd=cf.get("user","passwd")
        org_path=cf.get("user","path")
        hit_flag=cf.get("falg","HIT")
        tsinghua_flag=cf.get("falg","TSINGHUA")
        stl_flag=cf.get("falg","STL")
        hsbc_flag=cf.get("falg","HSBC")       
        
    except Exception as e:        
        logger.error("配置文件读取异常，请检查后重试（程序2s后退出）")
        logger.error(e)
        time.sleep(2)
        os._exit(0)
    
    #这样说明读取配置文件成功
    if(passwd!="cxk123456"  or user_name!="wangz"):
        print("账号或者密码错误，您不被授权使用本程序，即将关闭")
        time.sleep(5)
        os._exit(0)
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("读取配置文件成功！")
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("感谢用户{}使用本程序。".format(user_name))



    hsbc_path=org_path.strip("\\")+"\\HSBC"
    STL_path=org_path.strip("\\")+"\\STL"
    TSINGHUA_path=org_path.strip("\\")+"\\TSINGHUA"
    HIT_path=org_path.strip("\\")+"\\HIT"
    utsz_lecture_path=org_path.strip("\\")+"\\utsz_lecture"

    
    #print(error_key)
    #os.system("pause")

    ##从这里开始正式开始爬取
    after_list=[]

    if(hsbc_flag=="1"):
        logger.info("开始爬取汇丰讲座的全部信息")
        hsbc_time_list,hsbc_url_list,hsbc_title_list=wangz.get_HSBC_SEMINAR(HSBC_seminar)
            ###先去一遍有问题的
        for title in hsbc_title_list:
            title=title.strip()
            for error in error_key:
                if(error in title):
                    title=title.replace(error,"") 
            after_list.append(title)
        ##print(after_list)
        if str(os.path.exists(hsbc_path))=="false":
            os.makedirs(hsbc_path)
        for i in range(len(hsbc_time_list)):
            if not os.path.exists(hsbc_path+"\\"+after_list[i]):
                try:
                    os.makedirs(hsbc_path+"\\"+after_list[i])
                except:
                    while(len(logger.handlers)>2):
                        logger.handlers.pop()
                    logger.error("忽略错误异常的文件夹")
                    break
            wangz.get_HSBC_onehtml(hsbc_url_list[i],hsbc_path+"\\"+after_list[i],after_list[i],0)
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("汇丰所有讲座信息完成")





    after_list.clear()
    if(stl_flag=="1"):
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("开始爬取国际法学院讲座的全部信息")
        STL_url_list,STL_title_list,STL_info_list=wangz.get_STL_SEMINAR(law_school_url)
           ###先去一遍有问题的
        for title in STL_title_list:
            title=title.strip()
            for error in error_key:
                if(error in title):
                    title=title.replace(error,"") 
            after_list.append(title)
        #print(after_list)
        if os.path.exists(STL_path)==False:
            os.makedirs(STL_path)
        for i in range(len(STL_title_list)):
            if not os.path.exists(STL_path+"\\"+after_list[i]):
                try:
                    os.makedirs(STL_path+"\\"+after_list[i])
                except:
                    while(len(logger.handlers)>2):
                        logger.handlers.pop()
                    logger.error("忽略错误异常的文件夹")
                    break
            wangz.get_STL_one_html( STL_url_list[i],STL_path+"\\"+after_list[i],0)
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("国际法学院所有讲座信息完成")

    

    after_list.clear()
    if(tsinghua_flag=="1"):
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("开始爬取清华深研院讲座的全部信息")
        TSINGHUA_url_list,TSINGHUA_title_list=wangz.get_TSINGHUA_SEMINAR(TSINGHUA_url)
        after_list=[]
        ##先去一遍有问题的
        for title in TSINGHUA_title_list:
            title=title.strip()
            for error in error_key:
                if(error in title):
                    title=title.replace(error,"") 
            after_list.append(title)
    #print(after_list)
    #os.system("pause")
        if os.path.exists(TSINGHUA_path)==False:
            os.makedirs(TSINGHUA_path)
        for i in range(len(TSINGHUA_url_list)):
            #print(TSINGHUA_title_list[i][:-5].replace(":","_"))
            if not os.path.exists(TSINGHUA_path+"\\"+after_list[i]):
                try:
                    os.makedirs(TSINGHUA_path+"\\"+after_list[i])
                except:
                    while(len(logger.handlers)>2):
                        logger.handlers.pop()
                    logger.error("忽略错误异常的文件夹")
                    break
            wangz.get_TSINGHUA_one_html( TSINGHUA_url_list[i],TSINGHUA_path+"\\"+after_list[i],0)
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("清华深研院所有讲座信息完成")




    after_list.clear()
    if(hit_flag=="1"):
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("开始爬取哈工大讲座的全部信息")
        HIT_url_list,HIT_titel_list,HIT_info_list=wangz.get_HIT_SEMINAR(HIT_url)
        after_list=[]
    ##先去一遍有问题的
        for title in HIT_titel_list:
            title=title.strip()
            for error in error_key:
                if(error in title):
                    title=title.replace(error,"") 
            after_list.append(title)
    #print(after_list)
    #os.system("pause")
        if os.path.exists(HIT_path)==False:
            os.makedirs(HIT_path)
        for i in range(len(HIT_url_list)):
            #print(TSINGHUA_title_list[i][:-5].replace(":","_"))
            if not os.path.exists(HIT_path+"\\"+after_list[i]):
                try:
                    os.makedirs(HIT_path+"\\"+after_list[i])
                except:
                    while(len(logger.handlers)>2):
                        logger.handlers.pop()
                    logger.error("忽略错误异常的文件夹")
                    break
            wangz.get_HIT_one_html( HIT_url_list[i],HIT_info_list[i],HIT_path+"\\"+after_list[i],0)
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("哈工大所有讲座信息完成")

    while(len(logger.handlers)>2):
            logger.handlers.pop()
    logger.info("已经爬取要求的讲座信息")
    print("请到{}下查看".format(org_path))
    os.system("pause")
    os._exit(0)
    
    #while(len(logger.handlers)>2):
    #    logger.handlers.pop()
    #logger.info("开始爬取大学城讲座的全部信息")
    #utszlecture_url_list,utszlecture_titel_list,utszlecture_info_list=wangz.get_utszlecture_SEMINAR(utsz_lecture_url)
    #after_list=[]
    ###先去一遍有问题的
    #for title in utszlecture_titel_list:
    #    title=title.strip()
    #    for error in error_key:
    #        if(error in title):
    #            title=title.replace(error,"") 
    #    after_list.append(title)
    ##print(after_list)
    ##os.system("pause")
    #if os.path.exists(utsz_lecture_path)==False:
    #    os.makedirs(utsz_lecture_path)
    #for i in range(len(utszlecture_url_list)):
    #    #print(TSINGHUA_title_list[i][:-5].replace(":","_"))
    #    if not os.path.exists(utsz_lecture_path+"\\"+after_list[i]):
    #        try:
    #            os.makedirs(utsz_lecture_path+"\\"+after_list[i])
    #        except:
    #            while(len(logger.handlers)>2):
    #                logger.handlers.pop()
    #            logger.error("忽略错误异常的文件夹")
    #            break
    #    wangz.get_utszlecture_one_html( utszlecture_url_list[i],utszlecture_titel_list[i],utsz_lecture_path+"\\"+after_list[i],0)
    #while(len(logger.handlers)>2):
    #    logger.handlers.pop()
    #logger.info("大学城所有讲座信息完成")
