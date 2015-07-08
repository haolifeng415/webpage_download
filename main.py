#!/usr/bin/python 
#-*- coding:utf-8 -*-
from HTMLParser import HTMLParser
import urllib,os
import time
import argparse

(
    IMG,
    JS,
    CSS
) = range(3)
FILE_FOLDERS = ['img', 'js', 'css']

class MyHTMLParser(HTMLParser):
    '''
       解析html，将css js img文件的链接按类别存在list里 
    '''
    def __init__(self):
        HTMLParser.__init__(self)
        #存放img js css文件链接
        self.links_list =  [[],[],[]]
    def handle_starttag(self, tag, attrs):
#       print "Encountered the beginning of a %s tag" % tag
        if tag == 'img':
            for (variable, value)  in attrs:
                if variable == "src":
                    self.links_list[IMG].append(value)
        elif tag == 'script':
            for (variable, value)  in attrs:
                if variable == "src" or variable == 'href':
                    self.links_list[JS].append(value)
        elif tag == "link":
            dic = dict(attrs)
            if dic['rel']=="stylesheet":
                self.links_list[CSS].append(dic['href'])


def download(folder_path, html_code, durl, links_list):
    '''
        下载html中所加载的img js css等文件，并将其按类别存在不同的目录下，同时替换html中加载该文件的地址
        folder_path: 整个要存的大文件夹的路径
        html_code: 下载的页面html
        durl: 下载的html的url
        links_list:那些img js css资源文件的链接 
    '''
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        upurl = durl.rsplit('/',1)[0]

    index = 0
    for links in links_list:
        local_path = folder_path + '/' + FILE_FOLDERS[index]
        if not os.path.exists(local_path):
            os.mkdir(local_path)
        for link in links:
            #取资源文件名
            file_name = link.rsplit('/',1)[-1]
            file_name = file_name.split('?')[0]

            file_absolute_path = local_path + '/' + file_name
            if link[0:3] == '../':
                downlink = link[3:]
                download_url = upurl +'/' + downlink
            elif link[0:5] == 'http:' or link[0:6]=='https:':
                download_url = link
#                continue
            else:
                downlink = link
                download_url = durl + '/' + downlink
            try:
                urllib.urlretrieve(download_url, file_absolute_path)
            except Exception,error:
                print 'download error:' , error
            else:
                print 'download '+file_name
                #替换路径
                html_code = html_code.replace(link, FILE_FOLDERS[index]+'/'+file_name)
        index += 1
    open(folder_path+'/index.html', 'w').write(html_code)
    return True

def parse_option():
    parser = argparse.ArgumentParser(description='Download page from remote web',)
    #抓取数据时间间隔
    parser.add_argument('-d', dest='refresh_slot', type=int, default=60, help='reload webpage time slot')
    #url
    parser.add_argument('-u', dest='url', help='The web url')
    #保存的路径
    parser.add_argument('-o', dest='out_folder_path', default='/tmp', help='The folder path of the download page located')
    return parser.parse_args()

if __name__ == "__main__":
    option = parse_option()
    url = option.url
    refresh_slot = option.refresh_slot
    out_folder_path = option.out_folder_path

    if out_folder_path[-1]!='/':
        out_folder_path += '/'
    if not os.path.exists(out_folder_path):
        try:
            os.mkdir(out_folder_path)
        except Exception,error:
            print error
#    url = 'http://m.sohu.com'
    while 1:
        folder_path = out_folder_path + time.strftime('%Y%m%d%H%M')
        html_code = urllib.urlopen(url).read()
        hp = MyHTMLParser()
        hp.feed(html_code)
        hp.close()
        durl = url.rsplit('/',1)[0]
        download(folder_path, html_code, durl, hp.links_list)
        time.sleep(refresh_slot)
