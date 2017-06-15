# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:55:48 2014

@author: user
"""

from urllib.request import urlopen
from urllib.parse import urlparse
import re
import certifi
from bs4 import BeautifulSoup

# def extractIngredients(line):
#     ingredients = re.search(',"reviewPoint[.]+', line)
#
#     if (ingredients):
#         return ingredients

#Retrieves a list of all Internal links found on a page
def getInternalLinks(bsObj, includeUrl):
    includeUrl = urlparse(includeUrl).scheme+"://"+urlparse(includeUrl).netloc
    internalLinks = []
    #Finds all links that begin with a "/"
    # for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
    for link in bsObj.findAll("a", href=re.compile("^(\/kr\/ko\/ProductView\.do\?prdSeq\=.*)")):
        if link.attrs['href'] is not None:
            if (link.attrs['href'].startswith("/")):
                hrefValue = includeUrl + link.attrs['href']
            else:
                hrefValue = link.attrs['href']
            if hrefValue not in internalLinks:
                internalLinks.append(hrefValue)
    return internalLinks

# 이니스프리 신제품 페이지에서 각 제품 페이지 링크 정보
rootUrl = "http://www.innisfree.co.kr/ProductView.do?prdSeq=12878"
startingPage = "http://www.innisfree.com/kr/ko/ShopNewPrdList.do"
htmlFile = urlopen(startingPage, cafile=certifi.where())
bsObj = BeautifulSoup(htmlFile, "html.parser")
domain = urlparse(startingPage).scheme + "://" + urlparse(startingPage).netloc
internalLinks = getInternalLinks(bsObj, domain)

# 옵션 있는 페이지
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14940"]

# ingredient에 br, span 있는 경우 -> \r
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14742"]

# 5종
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=13438"]

for internalLink in internalLinks:
    htmlFile = urlopen(internalLink, cafile=certifi.where())
    bsObj = BeautifulSoup(htmlFile, "html.parser")
    try:
        # 솜 거르기
        expirationObj = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간'))
        if expirationObj == None:
            continue

        # 공산품 거르기
        expiration = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간')).parent.td.get_text()
        if "공산품" in expiration:
            continue

        #브랜드
        brand = bsObj.find("th", text=re.compile('제조자/제조판매원')).parent.td.get_text()
        brandTextList = brand.split("/")
        brandText = brandTextList[1]
        brandText = brandText.replace("(주)", "")
        brandText = brandText.replace("㈜", "").strip()

        # 성분
        ingredients = bsObj.find("p", text=re.compile('전성분 보기')).parent.div.get_text().strip()
        # '\r'이 있으면 마지막 라인만 프린트됨
        ingredients = ingredients.replace("\r", "")

        # 제품명
        productName = bsObj.find("div", id="pdtView")['prdnm'].strip()

        # 용량
        amount = bsObj.find("th", text=re.compile("용량 또는 중량")).parent.td.get_text().strip()

        #판매가
        # priceList = bsObj.find("p", id="pdtPrice")
        # for price in priceList:
        #     print(price.get_text().strip())
        price = bsObj.find(id="stdPrc")
        if price != None:
            price = price.get_text().strip()
        else:
            price = bsObj.find(id="pdtPrice")
            if price != None:
                price = price.find('span').get_text().strip()
            else:
                price = bsObj.find(id="sum")
                if price != None:
                    price = price.get_text().strip()


        print(internalLink)
        print(brandText)
        print(productName)
        print(ingredients)
        print(amount)
        print(price)

        # http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14940에서 작동하는 여러 옵션 상품
        # optionObjList = bsObj.findAll(name='input', attrs={'name': 'optionSelector'})
        # optionCodeList = []
        # optionNameList = []
        #
        # for optionObj in optionObjList:
        #     optionName = optionObj['kindnm']
        #     optionCode = re.search("[A-Z]+[0-9]+", optionName).group(0)
        #     optionCodeList.append(optionCode)
        #     optionNameList.append(optionName)

        # ingredientsOptionList = re.findall('\[[A-Z]+[0-9]+\]', ingredients)
        # ingredientsList = re.split("\[[A-Z]+[0-9]+\]", ingredients)
        # ingredientDict = {}
        # for i in range(0, len(ingredientsOptionList)):
        #     ingredientsOptionList[i] = ingredientsOptionList[i].replace("[", "")
        #     ingredientsOptionList[i] = ingredientsOptionList[i].replace("]", "")
        #     ingredientDict[ingredientsOptionList[i]] = ingredientsList[i+1].strip()
        # for i in range(0, len(optionCodeList)):
        #     print(optionNameList[i])
        #     print(ingredientDict[optionCode])

        # 옵션명
        optionObjList = bsObj.findAll(name='input', attrs={'name': 'optionSelector'})
        for optionObj in optionObjList:
            print(optionObj['kindnm'])

    except AttributeError as e:
        print(e)
        print(internalLink)



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

