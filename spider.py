# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 18:05:55 2015

@author: renzhexigua
"""
import requests
import bs4
import time
import pickle
import socket
import re
from functools import wraps
from multiprocessing import Pool, Manager, freeze_support, Process, current_process

# urlPrefix = "http://www.kuaidaili.com/free/"
urlPrefix = r"http://www.mayidaili.com/free/anonymous/高匿/"
# INHA = "inha"
# INTR = "intr"
# OUTHA = "outha"
# OUTTR = "outtr"

proxies = {
    "https": "182.18.19.222:3128",
}

def run():
    getIps()
    # getIps(INTR)
    # getIps(OUTHA)
    # getIps(OUTTR)


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
            (function.__name__, str(t1-t0))
            )
        return result
    return function_timer


@fn_timer
# def getIps(category=INHA):
def getIps():
    # pageTotal = getPageSum()
    # print("total is", pageTotal)
    pageTotal = 20
    pageIds = [i for i in range(1, pageTotal+1)]
    # print("len of is", len(pageIds))
    pool = Pool()
    pool.map(fetch, [(page, slaves) for page in pageIds])
    pool.close()
    pool.join()

    tmpList = [i for i in slaves]
    with open("slave.pk", mode="wb") as fslave:
        pickle.dump(tmpList, fslave)


# def getPageSum(category=INHA):
def getPageSum():
    resp = requests.get(urlPrefix, proxies=None)
    sp = bs4.BeautifulSoup(resp.text, "html.parser")
    # return int(sp.select("html body div#container div div#list div#listnav ul li")[-2].text)
    return int(sp.select("a")[-3].text)


def fetch(args):
    def getValidPort(content):
        styles = {}
        pattern = r'\w*{display:\w*}'
        for style in re.findall(pattern, str(content)):
            items = re.findall(r'\w{1,}', style)
            styles[items[0]] = 0 if items[-1] == 'none' else 1
        for port in content.select("span"):
            className = port.attrs['class'][0]
            if styles[className]:
                return port.text

    def fetchData(page, slaves):
        with open("ip.txt", mode="a") as fout:
            resp = requests.get(urlPrefix+"/"+str(page), proxies=None)
            sp = bs4.BeautifulSoup(resp.text, "html.parser")
            # ips = sp.select("html body div#container div div#list table.table.table-bordered.table-striped tbody tr")
            ips = sp.select("tbody tr")
            for ct in ips:
                ip = ct.select("td")[0].text
                port = getValidPort(ct.select("td")[1])
                slaves.append(ip+":"+port)
                # print(ip, port)
                # print(ip+":"+port, file=fout)

            # for item in ips:
            #     ip = item.text.split('\n')[1]
            #     port = item.text.split('\n')[2]
            #     slaves.append(ip+":"+port)

    fetchData(*args)

#
# def fetchData(category, page):
#     print("enter fetchData")
#     print(category, page)
#     with open("ip.txt", mode="a") as fout:
#         resp = requests.get(urlPrefix+category+"/"+str(page), proxies=None)
#         sp = bs4.BeautifulSoup(resp.text)
#         ips = sp.select("html body div#container div div#list table.table.table-bordered.table-striped tbody tr")
#         for item in ips:
#             ip = item.text.split('\n')[1]
#             port = item.text.split('\n')[2]
#             print(ip+":"+port, file=fout)


def loadSlave(slaves, validslaves):
    print("Load slaves proxies...")
    with open("slave.pk", mode="rb") as f:
        slaves.extend(pickle.load(f))
    for s in slaves:
        try:
            proxies = {"https": s}
            requests.get("http://www.baidu.com", timeout=1.5, proxies=proxies)
            validslaves.put(s)
            print("Valid:->", s)
        except socket.error or requests.exceptions.Timeout:
            print("invalid:->", s)
            pass
    # print("List:", len(slaves))
    # print("Queue:", validslaves.qsize())


if __name__ == "__main__":
    print(getPageSum())
    slaves = Manager().list()
    validslaves = Manager().Queue()
    # slaveProcess = Process(target=loadSlave, args=(slaves, validslaves, ))
    # slaveProcess.start()
    # slaveProcess.join()
    # print("Finish loading slaves")

    run()
