# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:55:48 2014

@author: user
"""

from urllib.request import urlopen
import re
import certifi
from bs4 import BeautifulSoup

# def extractIngredients(line):
#     ingredients = re.search(',"reviewPoint[.]+', line)
#
#     if (ingredients):
#         return ingredients


rootUrl = "http://www.innisfree.co.kr/ProductView.do?prdSeq=12878"
htmlFile = urlopen(rootUrl, cafile=certifi.where())
bsObj = BeautifulSoup(htmlFile, "html.parser")
ingredients = bsObj.find("div", text=re.compile('전성분')).parent.parent.td.div.get_text()
ingredients = ingredients.strip()
    # .get_text()
# for sibling in ingredients:
#     print(sibling)
print(ingredients)

# for elem in bsObj(text="전성분"):
#     # print(elem.parent.parent.next_sibling.child.get_text())
#     for child in elem.parent.parent.parent.children:
#         print(child)

# outFile = "/Users/jihyunson/PycharmProjects/crawlIngredients/성분.txt"
#
# fout = open(outFile, "w")
#
# for line in htmlFile:
#     if "전성" in line:
#         ingredients = extractIngredients(line)
#         if (ingredients != None):
#             # ingredients = productid.group().split("\"")
#             # print"inside:","http://reviews.sephora.com/8723Illuminate/"+onlyproductid[1]+"/reviews.htm?format=noscript"
#             # fout.write("http://reviews.sephora.com/8723Illuminate/" + onlyproductid[
#             #     1] + "/reviews.htm?format=noscript" + "\n");
#             fout.write(ingredients + "\n");
# fout.close()

