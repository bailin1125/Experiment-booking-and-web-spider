# -*- coding: utf-8 -*-
"""
Spyder Editor

All rights reserved from wangzhi 2019.8.27.
"""
#实验室预约抢位助手

import requests
import hashlib#哈希相关
import sys
import time
import configparser
import re
import base64
import logging
import webbrowser
from datetime import datetime
import os

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
#登录以及设备提交验证url
login_url="http://cem.ylab.cn/login.action"
valid_url="http://cem.ylab.cn/doLogin.action"
choose_instrument_url="http://cem.ylab.cn/user/listReserve.action?instrumentId="
vertify_url="http://cem.ylab.cn/user/verifyReserve.action"
do_reverse_url="http://cem.ylab.cn/user/doReserve.action"
#sure_url=""

#定义头部信息
User_Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
Referer="http://cem.ylab.cn/"
Content_Type="application/x-www-form-urlencoded"
header={}
header={'User-Agent':User_Agent,'Referer':Referer,'Content-Type':Content_Type}
#print(header)


#登录的post信息以及附加
login_post={}
login_post={"origUrl":"","origType":"",'rememberMe':"true",'username':"name",'password':"passwd"}


#vertify的post信息
vertify_data={"currentDate":"2019-08-31",
              "reserveDate":"2019年09月01日",
              "instrumentId": "e45f4c1c56d44e0e9ce469a9771e6828",
              "reserveStartTime": "17:00",
              "reserveEndTime": "17:30"
              }
#do_revsrese的post信息
do_reverse_data={"currentDate": "2019-08-31",
                 "reserveDate": "2019年09月01日",
                 "instrumentId": "e45f4c1c56d44e0e9ce469a9771e6828",
                 "reserveStartTime": "16:30",
                 "reserveEndTime": "18:00",
                 "hideRest": "1",
                 "testType": "自主测试",#测试方式，只有两种
                 "hopeDateTime": "2019-09-01",#期望时限
                 "ReserveName": "分析",#预约名称
                 "ProjectType": "电镜",#项目类型
                 "ReserveReport":"材料分析" #实验内容
                 }


#得到的仪器代码和对应，这里需要补充一些一起代码
instrument={}
instrument={"双束聚焦微纳加工仪FIB":"23ba4d2d9470434a905b4049ef457648",
            "场发射透射电镜F20-112(新F20)":"563e690aae7b41dfb6da1880f291e65b",
            "TITAN-149":"e45f4c1c56d44e0e9ce469a9771e6828",
            "场发射透射电镜F20-118（老F20）":"28ad18ae3ebb4f91b1d52553019ca381",
            "精密离子减薄仪PIPS II":"b7e445b11d72404f86cf0860414fe8b6",
            "球差校正电镜Titan":"7d43a6f731aa415594fca7ed3de8b935"}
#密码md5计算
def get_passwd_md5(passwd):
    passwd_bin=passwd.encode('utf-8')
    m=hashlib.md5()
    m.update(passwd_bin)
    return m.hexdigest()    

#用户名base64编码
def get_base64_loginname(name):
    name_b=base64.b64encode(name.encode('utf-8'))
    return name_b.decode('utf-8')

def make_sure_time(time1,start):
    time_str=time.strptime(time1+start,"%Y年%m月%d日%H:%M")
    reverse_col=time.mktime(time_str)
    now_clo=time.mktime(time.localtime())
    if(now_clo>reverse_col):
      logger.warning("不要预约已过去的时间，请检查config后重新提交")
      return False
    else:
      return True    
    
def get_time_col(time1,start):
    time_str=time.strptime(time1+start,"%Y-%m-%d%H:%M")
    return time.mktime(time_str)

def get_time_col_sec(time1,start):
    time_str=time.strptime(time1+start,"%Y-%m-%d%H:%M:%S")
    return time.mktime(time_str)
#然后要匹配几个关键时间
#pattern_titel=re.compile()#这个匹配标题
#pattern_head=re.compile()#这个匹配开始时间结束时间和时长
#pattern_time=re.compile()#匹配时间说明

copy_right='''All rights reserved from bailin
  version 2.0, plus new instruments information
  hope you enjoy it!'''
#正式开始搞了
if __name__=="__main__":
    #首先读取目录下面的配置文件
    print("{0:-^30}".format(copy_right))
    print("-----------------------------------------------------")
    print("\n\n\n")
    cf=configparser.ConfigParser()
    try:        
        cf.read("config.ini",encoding='utf-8')
        user_name=cf.get("user","name")
        passwd=cf.get("user","passwd")
        time1=cf.get("time","time1")
        start=cf.get("time","start")
        end=cf.get("time","end")        
        device_name=cf.get("device","name")
        testType=cf.get("book","testtype")
        reversename=cf.get("book","ReserveName")         
        projecttype=cf.get("book","ProjectType") 
        report=cf.get("book","ReserveReport") 
        action_ym_str=cf.get("book","actiontime_ym")
        action_hm_str=cf.get("book","actiontime_hm")
        
    except Exception as e:        
        logger.error("配置文件读取异常，请检查后重试（程序2s后退出）")
        logger.error(e)
        time.sleep(2)
        sys.exit()
    
    #这样说明读取配置文件成功
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("读取配置文件成功！")
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("感谢用户{}使用本程序。".format(user_name))
    
    #关于时间的说明
    #预约时间确认
    if(make_sure_time(time1,start)==False):
       while(len(logger.handlers)>2):
            logger.handlers.pop()
       logger.warning("程序将退出，请按任意字符。")
       sys.exit()    
    
    #下面开始正式进行网络信息提交
    s=requests.Session()
    login_post['username']=user_name
    login_post['password']=passwd
    #print(login_post)
    
    try:
        r=s.post(url=valid_url,headers=header,data=login_post,allow_redirects=True,timeout=30)
        #print(r.url)
        r.raise_for_status()
        r.encoding='utf-8'
        #print(type(r.text))
        #logger.debug(r.text)
        if(r.text.find("我的设备")!=-1):
            while(len(logger.handlers)>2):
                logger.handlers.pop()
            logger.info("登录预约系统成功，等待系统开放……")
        else:
            #logger.error("登录系统失败，请稍后尝试，按任意字符退出")
            sys.exit()
    except:
        #print(len(logger.handlers))
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("登录系统失败，请稍后尝试，按任意字符退出")
        sys.exit()      
       #打印出cookie的值
    for cookies in r.cookies.keys():
        logger.debug(cookies+":"+r.cookies.get(cookies)) 
        
    
    #确定最终提交的data  
    now_col=time.localtime()
    time_str= time.strftime("%Y-%m-%d",now_col)     
    do_reverse_data["currentDate"]=time_str
    do_reverse_data["reserveDate"]=time1
    do_reverse_data["instrumentId"]=instrument[device_name] 
    do_reverse_data["reserveStartTime"]=start
    do_reverse_data["reserveEndTime"]=end
    do_reverse_data ["hideRest"]="1"       
    do_reverse_data ["testType"]=testType
    do_reverse_data ["hopeDateTime"]=time_str
    do_reverse_data ["ReserveName"]=reversename
    do_reverse_data ["ProjectType"]=projecttype
    do_reverse_data ["ReserveReport"]=report 
    
    
    #先选择仪器，再预约时间，最后确定时间
    try:
        #选择仪器
        r=s.get(choose_instrument_url+instrument[device_name],headers=header,allow_redirects=True,timeout=30)
        r.raise_for_status()
        now=time.localtime()
        time_str=time.strftime("%Y-%m-%d",now)
        vertify_data["currentDate"]=time_str
        vertify_data["reserveDate"]=time1
        vertify_data["instrumentId"]=instrument[device_name]
        vertify_data["reserveStartTime"]=start
        vertify_data["reserveEndTime"]=end    
        #print(r.text)
        
        #先选定时间
        #r=s.post(vertify_url,headers=header,data=vertify_data,allow_redirects=True,timeout=30)
        #r.raise_for_status()
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("预约的仪器是：{}".format(device_name))
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("预约的时间段是：{},{}-{}".format(time1,start,end))
        #print(r.text)
        #开始自动预约系统生效时间确认
        #提前五秒钟就是
        action_col=get_time_col_sec(action_ym_str,action_hm_str)-12
        #print(action_col)
        actiontime_str=time.strftime("%Y-%m-%d,%H:%M:%S",time.localtime(action_col))
        actiontime_list=[]
        actiontime_list=time.strftime("%H:%M:%S",time.localtime(action_col)).split(":")
        real_action_list=[]
        for i in range(len(actiontime_list)):
            real_action_list.append(int(actiontime_list[i]))
            #print(real_action_list[i])
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.info("程序将于{}开始准备预约".format(actiontime_str))
        action_day=int(time.strftime("%Y-%m-%d",time.localtime(action_col)).split("-")[-1])
        #print("预订的日期是：{}".format(action_day))  
       # print(int(str(datetime.now()).split("-")[2].split()[0]))       
        #if(action_day!=int(str(datetime.now()).split("-")[2].split()[0])):
        #    while(len(logger.handlers)>2):
        #            logger.handlers.pop()
        #    logger.warning("预约暂不能跨天，请修改config")
        #    os.system("pause")
        #    sys.exit()
        while(True):
            time.sleep(1)
            now=datetime.now()
            hours=now.hour
            minutes=now.minute            
            second=now.second
            if(hours!=real_action_list[0] or minutes>real_action_list[1]  or action_day!=int(str(datetime.now()).split("-")[2].split()[0])): 
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.warning("未到对应小时或天数，休息5分钟")
                time.sleep(299)
                continue                 
            #print("{},{},{}".format(hours,minutes,second))
            if( hours==real_action_list[0] and minutes==real_action_list[1] and second>=real_action_list[2]):
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.info("将于10s后开始预约")
                for i in range(10):
                    time.sleep(1)
                    while(len(logger.handlers)>2):
                        logger.handlers.pop()
                    logger.info("{}s ".format(10-i))
                break
    except Exception as e:
        while(len(logger.handlers)>2):
            logger.handlers.pop()
        logger.error("网络不稳定，退出重试")
        time.sleep(1)
        sys.exit()
    
    #循环提交请求，直到预约成功
    i=1
    while(True):
        try:
            if(i==100):
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.error("尝试次数过多，失败退出！")
                break                
            while(len(logger.handlers)>2):
                logger.handlers.pop()
            logger.info("第{}次预约尝试……".format(i))
            r=s.post(do_reverse_url,data=do_reverse_data,headers=header,allow_redirects=True,timeout=30)
            r.encoding='utf-8'
            r.raise_for_status()
            ##print(r.text)
            ##os.system("pause")
            #fo=open("html1","w")
            #fo.write(r.text)
            #fo.close()
            if(r.text.find("预约成功")!=-1):
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.info("恭喜您，预约成功，请进入网页浏览器进行确认")
                break
            elif(r.text.find("预约失败")!=-1):
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.info("抱歉，其他人已经预约，请换个时间或仪器")
                break
            elif(r.text.find("不能预约")!=-1):
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.info("抱歉，您没有该仪器的使用权限，请切换仪器")
                break
            else:
                while(len(logger.handlers)>2):
                    logger.handlers.pop()
                logger.info("网络拥挤，正进行下次尝试……")
                i=i+1
                continue
        except:
            while(len(logger.handlers)>2):
                logger.handlers.pop()
            logger.debug("网络拥挤，正进行下次尝试……")
            i=i+1
            continue   
    os.system("pause")
    os._exit(0)
       
   
    
      
   
      
    
    
      
      
    
    
        
    




