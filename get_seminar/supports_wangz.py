from bs4 import BeautifulSoup
import requests
from requests_toolbelt import SSLAdapter
import time
import logging
import sys
import os
import re
import httplib2

#定义头部信息
User_Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
Referer={"HSBC":"https://www.phbs.pku.edu.cn/about/Allnews/seminar/index.html",
         "STL":"http://stl.pku.edu.cn/zh-hans/news/%E6%96%B0%E9%97%BB%E4%B8%AD%E5%BF%83/%E9%80%9A%E7%9F%A5%E5%85%AC%E5%91%8A/",
         "TSINGHUA":"http://www.sigs.tsinghua.edu.cn/xsdt/index.jhtml",
         "HIT":"http://www.hitsz.edu.cn/article/id-78.html",
         "utsz_lecture":"https://lib.utsz.edu.cn/media/css/style.css"}

Host={"HSBC":"www.phbs.pku.edu.cn",
      "STL":"stl.pku.edu.cn",
      "TSINGHUA":"www.sigs.tsinghua.edu.cn",
      "HIT":"www.hitsz.edu.cn",
      "utsz_lecture":"lib.utsz.edu.cn"}



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





def get_utszlecture_one_html(url,title,path,pic_id):
    ##这个的问题是chunked包错误，需要解决
    httplib2.http.client.HTTPConnection._http_vsn = 10
    httplib2.http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0' 
    httplib2.Response.version=10
    header={'User-Agent':User_Agent,"Host":Host["HIT"],'Referer':url}
    ##h=httplib2.Http(timeout=5)
    real_content=requests.get(url,headers=header,timeout=120)
    for i in range(10):
        print("第{}次尝试".format(i+1))
        try:
            real_content=requests.get(url,headers=header,timeout=5)
            print(resopnse)
            break
        except:
            continue
    soup=BeautifulSoup(real_content,"html.parser")
    
    ##先爬取一个标题    
    titel_file=open(path+"\\"+"title.txt","wt")      
    titel_file.write(title)
    titel_file.close()
    j=0   

    #然后是讲座信息等相关  
    img_content=soup.find("div",{"class":"edittext"})
    #print(img_content)
    #os.system("pause")
    if(img_content is not None):
        for url_small in img_content.find_all("img",{"src":re.compile("jpg|png")}):
            ura=url_small["src"]
            print(ura)
            #os.system("pause")
            pic_file1=open(path+"\\"+"pic_"+str(pic_id)+".jpg","wb")            
            pic_file1.write(requests.get(ura).content)
            #print("已写入：{}张图片".format(j+1))
            j+=1
            pic_id+=1
            pic_file1.close()
    #print(content)
    #然后是讲座内容
    words_content= soup.find("div",{"class":"edittext"})    
    if(words_content is not None):
        for item in words_content.find_all("p"):
            if(item.string is not None and item.string is not " "  and not("nbsq" in str(item.string))):
                #print(item.string)
                #os.system("pause")
                words_list.append(item.string)
        if(words_list):
            content_file=open(path+"\\content"+".txt","wt",encoding="utf-8")
            for line in words_list:
                line=line.encode("utf-8")
                line=line.decode("utf-8")
                content_file.write(line)
                content_file.write("\n")
            content_file.close()
    while(len(logger.handlers)>2):
           logger.handlers.pop()
    logger.warning("已完成爬取：{}".format(got_string))




def get_utszlecture_SEMINAR(org_url):
    content=BeautifulSoup(get_html(org_url,"utsz_lecture"),"html.parser")
    yugao=content.find("div",{"class":"leclistcon"})
    #print(yugao)    
    url_list=[]
    title_simple_list=[]
    info_list=[]

    for article in yugao.find_all("li"): 
        info=article.find("div",{"class":"text"})
        info_list.append(info.text)
        #os.system("pause")        
        title=article.find_all("a")[1]  
        title_simple_list.append(title.string)
        url_list.append("https://lib.utsz.edu.cn"+article.find("a")["href"])
            
    print(title_simple_list)
    print(url_list)
    print(info_list) 
    #os.system("pause") 
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("扫描大学城图书馆信息完毕，需要爬取{}场讲座信息".format(len(title_simple_list)))
    return url_list,title_simple_list,info_list



def get_HIT_one_html(url,info,path,pic_id):
    header={'User-Agent':User_Agent,'Referer':url,"Host":Host["HIT"]}
    content=get_html(url,"HIT")
    soup=BeautifulSoup(content,"html.parser")
    words_list=[]
    ##先爬取一个标题
    title=soup.find("div",{"class":"title"})
    titel_file=open(path+"\\"+"title.txt","wt")  
    got_string=title.string
    titel_file.write(got_string)
    titel_file.close()
    j=0

    ##打印讲座相关信息
    infow=open(path+"\\"+"information.txt","wt")
    infow.write(info)
    infow.close()

    #然后是讲座信息等相关  
    img_content=soup.find("div",{"class":"edittext"})
    #print(img_content)
    #os.system("pause")
    if(img_content is not None):
        for url_small in img_content.find_all("img",{"src":re.compile("jpg|png")}):
            ura=url_small["src"]
            if(ura[0]!='h'):
                ura="http://"+Host["HIT"]+ura
            ##print(ura)
            #os.system("pause")
            pic_file1=open(path+"\\"+"pic_"+str(pic_id)+".jpg","wb")            
            pic_file1.write(requests.get(ura,headers=header).content)
            #print("已写入：{}张图片".format(j+1))
            j+=1
            pic_id+=1
            pic_file1.close()
    #print(content)
    #然后是讲座内容
    words_content= soup.find("div",{"class":"edittext"})
    #print(words_content)
    #os.system("pause")
    if(words_content is not None):
        for item in words_content.find_all("p"):
            if(item.string is not None and item.string is not " "  and not("nbsq" in str(item.string))):
                #print(item.string)
                #os.system("pause")
                words_list.append(item.string)
        if(words_list):
            content_file=open(path+"\\content"+".txt","wt",encoding="utf-8")
            for line in words_list:
                line=line.encode("utf-8")
                line=line.decode("utf-8")
                content_file.write(line)
                content_file.write("\n")
            content_file.close()
    while(len(logger.handlers)>2):
           logger.handlers.pop()
    logger.warning("已完成爬取：{}".format(got_string))


def get_HIT_SEMINAR(org_url):
    content=BeautifulSoup(get_html(org_url,"HIT"),"html.parser")
    yugao=content.find("ul",{"class":"lecture_n"})
    #print(yugao)
    
    url_list=[]
    title_simple_list=[]
    info_list=[]

    for article in yugao.find_all("li"): 
        info=article.find_all("div")[2]
        info_list.append(info.text)
        #os.system("pause")        
        title=article.find("a")  
        title_simple_list.append(title.string)
        url_list.append("http://www.hitsz.edu.cn"+article.find("a")["href"])
    #os.system("pause")          
    #print(title_simple_list)
    #print(url_list)
    #print(info_list)
    #print(info_list)      
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("扫描哈工大信息完毕，需要爬取{}讲座信息".format(len(title_simple_list)))
    return url_list,title_simple_list,info_list



def get_TSINGHUA_one_html(url,path,pic_id):
    content=get_html(url,"TSINGHUA")
    soup=BeautifulSoup(content,"html.parser")
    start_url="http://www.sigs.tsinghua.edu.cn"#/u/cms/cnsyy/201908/14171130qrea.png
    ##先爬取一个标题
    title=soup.find("span",{"class":"title"})
    titel_file=open(path+"\\"+"title.txt","wt")  
    got_string=title.string
    titel_file.write(got_string)
    titel_file.close()
    j=0
    #然后是讲座信息等相关  
    
    for url_small in soup.find_all("img",{"src":re.compile("jpg|png")}):
         ura=url_small["src"]
         #print(ura)
        # os.system("pause")
         pic_file1=open(path+"\\"+"pic_"+str(pic_id)+".jpg","wb")
         pic_file1.write(requests.get(start_url+ura).content)
         #print("已写入：{}张图片".format(j+1))
         j+=1
         pic_id+=1
         pic_file1.close()
    #print(content)    
    while(len(logger.handlers)>2):
           logger.handlers.pop()
    logger.warning("已完成爬取：{}".format(got_string))




def get_TSINGHUA_SEMINAR(org_url):
    content=BeautifulSoup(get_html(org_url,"TSINGHUA"),"html.parser")
    yugao=content.find("ul",{"class":"newslist"})
    #print(yugao)
    
    url_list=[]
    title_simple_list=[]

    for article in yugao.find_all("li"):         
        title=article.find("span",{"class":"title"})  
        title_simple_list.append(title.string)
        url_list.append(article.find("a")["href"])
              
    #print(title_simple_list)
    #print(url_list)
    #print(info_list)  
    #os.system("pause") 
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("扫描清华信息完毕，需要爬取{}讲座信息".format(len(title_simple_list)))
    return url_list,title_simple_list


def get_time_col(time_a):
    time_str=time.strptime(time_a,"%Y-%m-%d")
    return time.mktime(time_str)



def get_STL_one_html(url,path,pic_id):
    ##print(url)
    content=get_html(url,"STL")
    soup=BeautifulSoup(content,"html.parser")
    j=0
    ##先爬取一个标题
    title=soup.find("article")
    titel_file=open(path+"\\"+"title.txt","wt")  
    got_string=title.find("h1").string
    titel_file.write(got_string)
    titel_file.close()
    #然后是讲座信息等相关
    content=[]
    try:
        for i in title.find("blockquote").find_all("p"):          
            if i.string !="" and i.string !='\xa0' and i.string!=None:
                content.append(i.string)     
             #print(i.string)
    except:
        for i in title.find_all("p"):          
            if i.string !="" and i.string !='\xa0' and i.string!=None:
                content.append(i.string)  
    
    for url_small in title.find_all("a",{"href":re.compile("jpg")}):
         ura=url_small["href"]          
         pic_file1=open(path+"\\"+"pic_"+str(pic_id)+".jpg","wb")
         pic_file1.write(requests.get(ura).content)
         #print("已写入：{}张图片".format(j+1))
         j+=1
         pic_id+=1
         pic_file1.close()
    #print(content)
    content_file=open(path+"\\content"+".txt","wt",encoding="utf-8")
    for line in content:
        #line=line.encode("utf-8")
        #line=line.decode("utf-8")
        content_file.write(line)
        content_file.write("\n")
    content_file.close()
    while(len(logger.handlers)>2):
           logger.handlers.pop()
    logger.warning("已完成爬取：{}".format(got_string))




def get_STL_SEMINAR(org_url):  ##返回每个讲座的url，小标题以及时间地点信息
    content=BeautifulSoup(get_html(org_url,"STL"),"html.parser")
    yugao=content.select(".uk-width-medium-7-10")[0]
    #print(yugao)
    key_words=["活动","讲座","分享","预告"]

    info_list=[]
    url_list=[]
    title_simple_list=[]

    for article in content.find_all("article"):        
        title=article.find("a").string
        for key in key_words:
            if(key in title):
                title_simple_list.append(title)
                #print(article)
                url_list.append(article.find("a")["href"])
                try:
                    info_list.append(article.find("blockquote").find("p").string)
                    ##有时候信息不写在对应里面
                except:
                    ##print(article.find_all("p")[0].string)
                    info_list.append(article.find_all("p")[0].string)
                break
    #print(title_simple_list)
    #print(url_list)
    #print(info_list)  
    #os.system("pause") 
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("扫描国法信息完毕，需要爬取{}讲座信息".format(len(title_simple_list)))
    return url_list,title_simple_list,info_list
 
def get_HSBC_SEMINAR(org_url):
    content=BeautifulSoup(get_html(org_url,"HSBC"),"html.parser")
    yugao=content.select(".little-main-list")[0]
    #print(yugao)
    time_list=[]
    url_list=[]
    title_simple_list=[]
    ##这里我们要做一个限制，需要只统计以后的时间
    now=time.localtime()
    ##时间的统计
    for time_a in yugao.find_all("span")[:-1]:
        #print(time_a.string)
        #if(time.mktime(now)>get_time_col(time_a.string)):
        #    break
        time_list.append(time_a.string)
    ##网址的统计
    for urll_a in yugao.find_all("a"):
        #print(urll_a["href"])       
        url_list.append(urll_a["href"])
        if(len(time_list)==len(url_list)):
            break
    ##简略标题的统计
    for sample_title in yugao.find_all("h2"):
        #print(sample_title.string)
        title_simple_list.append(sample_title.string)
        if(len(time_list)==len(title_simple_list)):
            break
    while(len(logger.handlers)>2):
        logger.handlers.pop()
    logger.info("扫描汇丰信息完毕，需要爬取{}讲座信息".format(len(time_list)))
    return time_list,url_list,title_simple_list
    

    #list_reg=re.compile("<span>2019.+</span>")
    #time_list=re.findall(list_reg,str(content))
    #print(time_list)


def get_html(url,name):
    header={'User-Agent':User_Agent,'Referer':Referer[name],"Host":Host[name]}
    try:
        requests.adapters.DEFAULT_RETRIES=5
        s=requests.session()
        s.keep_alive=False
        try:
            html=s.get(url,timeout=30,headers=header)            
            html.encoding=html.apparent_encoding
            html.raise_for_status()
        except:
            adapter=SSLAdapter('TLSv1')
            s.mount('https://',adapter)
            html=s.get(url,verify=False,timeout=30,headers=header) 
            html.raise_for_status()
        html.raise_for_status()
        content=html.text
        return content       
    except Exception as e:
        logger.error("访问网址出错，请检查后再试")
        logger.error(e)
        time.sleep(3)
        sys.exit(0)
    return None

##

def get_HSBC_onehtml(url,path,txt_id,pic_id):    ##需要的url，生成的路径，产生的内容文件名字，图片的递增序列
     content=get_html(url,"HSBC")
     soup=BeautifulSoup(content,"html.parser")
     j=0
     ##先爬取一个标题
     title=soup.select(".bold")[1]
     titel_file=open(path+"\\"+"title.txt","wt")     
     titel_file.write(title.string)
     titel_file.close()
     #然后是讲座信息等相关
     content=[]
     for i in soup.select(".article-content"): 
          for abstract in i.find_all("p"):
              if abstract.string !=None and abstract.string !='\xa0':
                  content.append(abstract.string)
              #print(abstract.string)
          for url_small in i.find_all("img"):
              ura=url_small["src"]                
              pic_file1=open(path+"\\"+"pic_"+str(pic_id)+".jpg","wb")
              ##print(ura)
              if("img-user"in ura):
                  continue
              pic_file1.write(requests.get(ura).content)
              #print("已写入：{}张图片".format(j+1))
              j+=1
              pic_id+=1
              pic_file1.close()
     #print(content)
     content_file=open(path+"\\"+txt_id+".txt","wt",encoding="utf-8")
     for line in content:
         line=line.encode("utf-8")
         line=line.decode("utf-8")
         content_file.write(line)
         content_file.write("\n")
     content_file.close()
     while(len(logger.handlers)>2):
            logger.handlers.pop()
     logger.warning("已完成爬取：{}".format(title.string))
