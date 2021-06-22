#! /usr/bin/env python
# -*- coding:utf-8   -*-
# __author__ == "albert"

from multiprocessing import Pool
import logging
from logging import handlers
import os
import time
import requests
import threading
import re

# logging.basicConfig(level = logging.DEBUG,filename='new.log', filemode='w', format = '%(asctime)s %(filename)s:%(lineno)s %(funcName)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
logging.root.setLevel(logging.DEBUG)
logFormat = logging.Formatter(
    '%(asctime)s %(filename)s:%(lineno)s %(funcName)s %(levelname)s %(message)s')

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logFormat)
logger.addHandler(sh)

# th = handlers.TimedRotatingFileHandler(filename='new.log',when='D',backupCount=3,encoding='utf-8')
fh = logging.FileHandler('get.log', mode='w', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logFormat)
logger.addHandler(fh)

proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809",
}

cookies = {
    'existmag': 'all'
}

thread_interval = 0.1
rootPath = "./cover/"


def imgdownload(imgurl, path, imgname):
    # if not os.path.exists(path):
    #     os.mkdir(path)
    try:
        imgres = requests.get(imgurl, proxies=proxies, cookies=cookies)
    except requests.exceptions.ProxyError:
        logger.error("proxy error, download img failed,url="+imgurl)
        # return "proxy error, download img fail"
    except Exception as e:
        logger.error(e)
    else:
        filename = path+'\\'+imgname
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(imgres.content)
                f.close()
                logger.info(imgname + " download success")
        else:
            pass
            logger.info(imgname + " already exist")
    finally:
        pass


def parsehtml(content):
    title_patten = re.compile(r'\<title\>(.*)\ - JavBus\</title\>')
    fanhao_patten = re.compile(
        r'識別碼:</span> <span style="color:#CC0000;">(.*)</span>')
    cover_patten = re.compile(r'bigImage" href="(.*jpg)">')

    result = re.search(title_patten, content)
    title = result.groups(1)
    result = re.search(fanhao_patten, content)
    if result:
        fanhao = result.groups(1)
        result = re.search(cover_patten, content)
        cover = result.groups(0)
        return title[0], fanhao[0], cover[0]
    else:
        return None, None, None


def parseUrlAndDownloadCover(url, folder, fanhao, checkSingle):
    try:
        res = requests.get(url, proxies=proxies, cookies=cookies)
    except requests.exceptions.ProxyError:
        logger.error("proxy error, get page failed, url=" + url)
        # return "get page error " + url
    except Exception as e:
        logger.error(e)
    else:
        patten404 = re.compile(r'404 Page Not Found')
        result404 = re.search(patten404, res.text)
        if result404:
            logger.warning("found 404 " + url)
            return

        res.encoding = 'utf-8'
        single_patten = re.compile(r'star-name')
        result = re.findall(single_patten, res.text)
        # logger.info(len(result))
        if checkSingle and len(result) > 2:
            # logger.info(fanhao + " not single")
            return

        title, fanhao, cover = parsehtml(res.text)
        if title and fanhao:
            cover_url="https://www.javbus.com"+cover
            imgdownload(cover_url, folder, fanhao+'.jpg')
            # return ret
        else:
            logger.warning("can't find fanhao, maybe 404, url="+url)
            # return
    finally:
        pass


def downloadSpecImg(fanhao, path, checkSingle):
    filename = path+'/'+fanhao+'.jpg'
    if not os.path.exists(filename):
        url = "https://www.javbus.com/"+fanhao
        parseUrlAndDownloadCover(url, path, fanhao, checkSingle)
    else:
        # logger.info(fanhao+" file already exist")
        pass

def downloadImgBatch(fanhao, path, checkSingle):
    p = Pool()
    p.apply_async(downloadSpecImg, args=(fanhao, path, checkSingle))
    p.close()
    p.join()


def parseUrlListAndThreadDownload(url, name, checkSingle):
    try:
        res = requests.get(url, proxies=proxies, cookies=cookies)
    except requests.exceptions.ProxyError:
        logger.error("proxy error, get page failed " + url)
    except:
        pass
    else:
        res.encoding = 'utf-8'
        urlpatten = re.compile(r'<a class="movie-box" href="(.*)">')
        result = re.findall(urlpatten, res.text)
        if result:
            for tempurl in result:
                # print(tempurl)
                fanhaoPatten = re.compile(r'https://www.javbus.com/(.+)$')
                fanhaoResult = re.search(fanhaoPatten, tempurl)
                if fanhaoResult:
                    fanhao = fanhaoResult.group(1)
                    filename = name+'/'+fanhao+'.jpg'
                    if os.path.exists(filename):
                        logger.info(fanhao+" already exist")
                        pass
                    else:
                        new_thread = threading.Thread(
                            target=parseUrlAndDownloadCover, args=(tempurl, name, fanhao, checkSingle))
                        new_thread.start()
                        time.sleep(thread_interval)
                else:
                    logger.info("can't find fanhao, " + tempurl)
    finally:
        pass


def autoParseUrlListAndThreadDownload(url, name, checkSingle):
    try:
        res = requests.get(url, proxies=proxies, cookies=cookies)
    except requests.exceptions.ProxyError:
        logger.error("proxy error, get page failed " + url)
    except Exception as e:
        logger.error(e)
    else:
        res.encoding = 'utf-8'
        if name == "":
            titlePatten = re.compile(r'<title>(第\d+頁 - )*(.*) -.+- 影片</title>')
            titleResult = re.search(titlePatten, res.text)
            if titleResult:
                name = titleResult.group(2)
                print(name)
            else:
                print("something is wrong, can't find title")
                return
        path = rootPath + name
        if not os.path.exists(path):
            os.makedirs(path)

        urlpatten = re.compile(r'<a class="movie-box" href="(.*)">')
        result = re.findall(urlpatten, res.text)
        if result:
            for tempurl in result:
                # print(tempurl)
                fanhaoPatten = re.compile(r'https://www.javbus.com/(.+)$')
                fanhaoResult = re.search(fanhaoPatten, tempurl)
                if fanhaoResult:
                    fanhao = fanhaoResult.group(1)
                    filename = path+'/'+fanhao+'.jpg'
                    if os.path.exists(filename):
                        # logger.info(fanhao+" already exist")
                        pass
                    else:
                        new_thread = threading.Thread(
                            target=parseUrlAndDownloadCover, args=(tempurl, path, fanhao, checkSingle))
                        new_thread.start()
                        time.sleep(thread_interval)
                else:
                    logger.warning("can't find fanhao, " + tempurl)

        nextPatten = re.compile(r'<a id="next" href="(.*)">下一頁</a>')
        nextResult = re.search(nextPatten, res.text)
        if nextResult:
            nextPage = "https://www.javbus.com" + nextResult.group(1)
            autoParseUrlListAndThreadDownload(nextPage, name, checkSingle)

    finally:
        pass


def findByNameAndDownloadImage(name, code, page, checkSingle):
    path = './'+name+'/'
    if not os.path.exists(path):
        os.mkdir(path)

    p = Pool()
    for i in range(1, page):
        url = "https://www.javbus.com/star/"+code + "/"+str(i)

        p.apply_async(parseUrlListAndThreadDownload,
                      args=(url, name, checkSingle))
    p.close()
    p.join()


def autoParseAndDownloadImage(url, checkSingle=True):
    # if not checkSingle:
    #     checkSingle = True
    seriesPatten = re.compile(r'https://www.javbus.com/(.*)/.*')
    seriesResult = re.search(seriesPatten, url)
    if seriesResult:
        series = seriesResult.group(1)
        if series == "series":
            checkSingle = False
    autoParseUrlListAndThreadDownload(url, "", checkSingle)


def downloadFanhaoImg(xilie, start_num, end_num):
    for i in range(start_num, end_num):
        path = rootPath + xilie
        if not os.path.exists(path):
            os.makedirs(path)

        fanhao = xilie + '-' + str(i).zfill(3)
        new_thread = threading.Thread(
            target=downloadSpecImg, args=(fanhao, path, False))
        new_thread.start()
        time.sleep(0.3)


def batchDownloadByUrl(urls):
    for url in urls:
        # print(url)
        autoParseAndDownloadImage(url)


if __name__ == '__main__':

    urls = [
        # "https://www.javbus.com/series/xk",
        "https://www.javbus.com/star/x2w",
        # "https://www.javbus.com/genre/5t",
    ]

    batchDownloadByUrl(urls)

    # arrays = ["MIDE-332", "MIDE-345","MIDE-404","MIDE-436","MIDE-495","MIMK-045","PPPD-431","PPPD-439","REBDB-332","WANZ-744",]
    # for fanhao in arrays:
    #     new_thread = threading.Thread(target=downloadSpecImg,args=(fanhao,"temp", False))
    #     new_thread.start()

    # downloadFanhaoImg("TRE", 100, 200)
