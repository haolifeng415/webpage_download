#!/usr/bin/python 
#coding:utf-8
from HTMLParser import HTMLParser
import urllib,os
import sys
reload(sys)
sys.setdefaultencoding('gbk')

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
    parser.add_argument('-d', dest='refresh_slot', action='store_true')
    #url
    parser.add_argument('-u', dest='url', action='store_true')
    #保存的路径
    parser.add_argument('-o', dest='directory', action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
#    option = parse_option()
#    #修复所有
#    flush_profile_inconsistence(option.dry_run)
#    url = option.url
#    refresh_slot = option.refresh_slot
    url = 'http://m.sohu.com'
    folder_path = '/tmp/hao'
    html_code = urllib.urlopen(url).read()
    hp = MyHTMLParser()
    hp.feed(html_code)
    hp.close()
    durl = url.rsplit('/',1)[0]
    download(folder_path, html_code, durl, hp.links_list)
