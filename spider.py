# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 18:05:55 2015

@author: renzhexigua
"""
import requests
import bs4
import time
from functools import wraps
from multiprocessing import Pool

urlPrefix = "http://www.kuaidaili.com/free/"
INHA = "inha"
INTR = "intr"
OUTHA = "outha"
OUTTR = "outtr"

proxies = {
    "http": "171.38.75.176:8123",
}

def run():
    getIps(INHA)
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
def getIps(category=INHA):
    print("get total")
    pageTotal = getPageSum(category)
    print("total is", pageTotal)
    pageIds = [i for i in range(1, pageTotal+1)]
    print("len of is", len(pageIds))
    pool = Pool(1)
    print("before pool")
    result = pool.map(fetch, [(category, page) for page in pageIds])
    # fetchData(category, pageTotal)
    print(category, "has", pageTotal, "pages")


def getPageSum(category=INHA):
    resp = requests.get(urlPrefix+category, proxies=proxies)
    sp = bs4.BeautifulSoup(resp.text)
    return int(sp.select("html body div#container div div#list div#listnav ul li")[-2].text)


def fetch(args):
    print("enter fetch")
    def fetchData(category, page):
        print("enter fetchData")
        print(category, page)
        with open("ip.txt", mode="a") as fout:
            resp = requests.get(urlPrefix+category+"/"+str(page), proxies=proxies)
            sp = bs4.BeautifulSoup(resp.text)
            ips = sp.select("html body div#container div div#list table.table.table-bordered.table-striped tbody tr")
            for item in ips:
                ip = item.text.split('\n')[1]
                port = item.text.split('\n')[2]
                print(ip+":"+port, file=fout)
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


if __name__ == "__main__":
    print("start")
    run()