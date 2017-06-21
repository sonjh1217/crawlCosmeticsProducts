# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:55:48 2014

@author: user
"""
import time
from urllib.request import urlopen
from urllib.parse import urlparse
import re
import certifi
from bs4 import BeautifulSoup
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Retrieves a list of all Internal links found on a page
def addInternalLinks(internalLinksParam, bsObj, includeUrl):
    includeUrl = urlparse(includeUrl).scheme+"://"+urlparse(includeUrl).netloc
    # Finds all links that begin with a "/"
    # for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
    for link in bsObj.findAll("a", href=re.compile("[^a-z]productView.+", flags=re.IGNORECASE)):
        if link.attrs['href'] is not None:
            if link.attrs['href'].startswith("/"):
                hrefValue = includeUrl + link.attrs['href']
            elif link.attrs['href'].startswith('javascript'):
                hrefValue = link.attrs['href'].replace("javascript:productView('", 'http://www.etude.co.kr/product.do?method=view&prdCd=').replace("');", '')
            else:
                hrefValue = link.attrs['href']

            if hrefValue not in internalLinksParam:
                internalLinksParam.append(hrefValue)
                print("number of links: " + str(len(internalLinksParam)))
    return internalLinksParam

# #Retrieves a list of Internal links not in previous links found on a page
# def getNewInternalLinks(bsObj, includeUrl, previousLinks):
#     includeUrl = urlparse(includeUrl).scheme+"://"+urlparse(includeUrl).netloc
#     internalLinks = []
#     #Finds all links that begin with a "/"
#     # for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
#     for link in bsObj.findAll("a", href=re.compile("^(\/kr\/ko\/ProductView\.do\?prdSeq\=.*)")):
#         if link.attrs['href'] is not None:
#             if (link.attrs['href'].startswith("/")):
#                 hrefValue = includeUrl + link.attrs['href']
#             else:
#                 hrefValue = link.attrs['href']
#             if hrefValue not in internalLinks and hrefValue not in previousLinks:
#                 internalLinks.append(hrefValue)
#     return internalLinks

def getLinksFrom(startingPageParam):
    # 보이는 웹드라이버(크롬)
    driver = webdriver.Chrome(executable_path='/Users/JihyunSon/Documents/chromedriver')
    # 보이지 않는 웹드라이버
    # driver = webdriver.PhantomJS(executable_path='/Users/JihyunSon/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')
    # 첫 페이지를 로드한다
    driver.get(startingPageParam)
    domain = urlparse(startingPageParam).scheme + "://" + urlparse(startingPage).netloc
    currentPageNum = 1
    internalLinkList = []
    try:
        # 다음 페이지 버튼이 clickable해지는 순간을 기다린다. 10은 time-out을 의마한다
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, str(currentPageNum + 1))))
    finally:
        pageSource = driver.page_source
        print("currentPageNum: " + str(currentPageNum))

        bsObj = BeautifulSoup(pageSource, "html.parser")
        internalLinkList = addInternalLinks(internalLinkList, bsObj, domain)

        # 다음 페이지 숫자를 가진 버튼이 있다면 계속한다
        while len(driver.find_elements(By.LINK_TEXT, str(currentPageNum + 1))) > 0:
            driver.find_element(By.LINK_TEXT, str(currentPageNum + 1)).click()
            # driver.find_element(By.XPATH, "//a[@class='pagingNum' and text()='" + str(currentPageNum + 1) + "']").click()#스크롤을 내리긴 하는데 클릭이 안됨. 클릭할 게 1개인데도 클릭을 안 하고 finally로 넘어간다

            # click과 wait이 겹쳐져 오작동할 떄가 있어 불가피하게 implicit_wait을 활용하였다
            time.sleep(2)

            try:
                # 다음 페이지가 로드되기를 기다린다 2 페이지일 경우 텍스트가 2인 strong 태그가 있다
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//strong[text()=" + str(currentPageNum + 1) + "]")))
            finally:
                #로드 완료
                currentPageNum += 1
                print("currentPageNum: " + str(currentPageNum))

                pageSource = driver.page_source
                bsObj = BeautifulSoup(pageSource, "html.parser")
                internalLinkList = addInternalLinks(internalLinkList, bsObj, domain)

    driver.quit()
    return internalLinkList

#
# #csv 파일에 저장된 데이터 읽기
# outFile = "/Users/jihyunson/PycharmProjects/crawlIngredients/url.csv"
# with open(outFile, "r") as csvfile:
#     reader = csv.reader(csvfile)
#     previousLinks = list(reader)[0]
# internalLinks = previousLinks
#
#
# 이니스프리 신제품 페이지에서 각 제품 페이지 링크 정보
# startingPage = "http://www.innisfree.com/kr/ko/ShopNewPrdList.do"
startingPage = "http://www.etude.co.kr/product.do?method=new"
# 카테고리
# startingPage = "http://www.innisfree.com/kr/ko/Product.do?catCd01=UA"
internalLinks = getLinksFrom(startingPage)
# internalLinks = getNewInternalLinks(bsObj, domain, previousLinks)
#
# #추후 데이터를 중복해서 뽑지 않기 위해 url data를 저장한다
# outFile = "/Users/jihyunson/PycharmProjects/crawlIngredients/url.csv"
# with open(outFile, "w") as urlFile:
#     wr = csv.writer(urlFile, quoting=csv.QUOTE_ALL)
#     wr.writerow(internalLinks)

# 제주 조릿대 롤온 쿨링스킨 (옵션 없는 페이지)
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14998"]

# 옵션 있는 페이지
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14940"]

# 공산품
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=15096"]

# ingredient 에 br, span 있는 경우 -> \r
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=14742"]

# 5종
# internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=13438"]

# 에뛰드
# internalLinks = ["http://www.etude.co.kr/product.do?method=view&prdCd=101004084"]

# 에뛰드 케이스
# internalLinks = ["http://www.etude.co.kr/product.do?method=view&prdCd=102005116"]

# 파일로 저장하기
with open('skinProducts2.csv', 'w') as csvfile:
    fieldnames = ['brand', 'category1', 'category2', 'product', 'options', 'price', 'amount', 'ingredients', 'image', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for internalLink in internalLinks:
        htmlFile = urlopen(internalLink, cafile=certifi.where())
        bsObj = BeautifulSoup(htmlFile, "html.parser")
        try:
            # 제품 요약 정보 이용
            # 솜 거르기
            # expirationObj = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간'))
            expirationObj = bsObj.find("th", text=re.compile('사용기한'))
            if expirationObj is None:
                continue

            # 공산품 거르기
            # expiration = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간')).parent.td.get_text()
            expiration = bsObj.find("th", text=re.compile('사용기한')).parent.td.get_text()
            if "공산품" in expiration or len(expiration.strip()) == 0:
                continue

            # 브랜드
            # brand = bsObj.find("th", text=re.compile('제조자/제조판매원')).parent.td.get_text()
            brand = bsObj.find("th", text=re.compile('제조')).parent.td.get_text()
            brandTextList = brand.split("/")
            brandText = brandTextList[-1]
            brandText = brandText.replace("(주)", "")
            brandText = brandText.replace("㈜", "").strip()

            # 용량
            amount = bsObj.find("th", text=re.compile("용량")).parent.td.get_text().strip()

            # 성분
            # 이니스프리
            if "innisfree" in internalLink:
                ingredients = bsObj.find("p", text=re.compile('전성분 보기')).parent.div.get_text().strip()
            # # '\r'이 있으면 마지막 라인만 프린트됨
            # ingredients = ingredients.replace("\r", "")

            # 에뛰드
            elif "etude" in internalLink:
                ingredients = bsObj.find(alt=re.compile('전성분$')).parent.parent.get_text().strip()

            # 옵션별로 끊어서 옵션: 성분으로 딕셔너리 만들기
            # ingredientsOptionList = re.findall('\[[A-Z]+[0-9]+\]', ingredients)
            # ingredientsList = re.split("\[[A-Z]+[0-9]+\]", ingredients)
            # ingredientDict = {}
            # print(len(ingredientsOptionList))
            # print(len(ingredientsList))
            # for i in range(0, len(ingredientsOptionList)):
            #     ingredientsOptionList[i] = ingredientsOptionList[i].replace("[", "")
            #     ingredientsOptionList[i] = ingredientsOptionList[i].replace("]", "")
            #     ingredientDict[ingredientsOptionList[i]] = ingredientsList[i + 1].strip()
            # print(ingredientDict)
            # 제품 요약 정보 이용

            # meta 이용
            # 제품명
            # productName = bsObj.find("div", id="pdtView")['prdnm'].strip()

            productNameObj = bsObj.find(property="rb:itemName")
            if productNameObj is not None:
                productName = productNameObj['content'].strip()
            else:
                productNameString = bsObj.title.get_text()
                productNameList = productNameString.split("-")
                productName = productNameList[-1]

            # 제품 이미지
            productImage = bsObj.find(property=re.compile('image', flags=re.IGNORECASE))['content']

            # 판매가
            # priceList = bsObj.find("p", id="pdtPrice")
            # for price in priceList:
            #     print(price.get_text().strip())

            # price = bsObj.find(id="stdPrc")
            # if price != None:
            #     price = price.get_text().strip()
            # else:
            #     price = bsObj.find(id="pdtPrice")
            #     if price != None:
            #         price = price.find('span').get_text().strip()
            #     else:
            #         price = bsObj.find(id="sum")
            #         if price != None:
            #             price = price.get_text().strip()
            priceObj = bsObj.find(property="rb:originalPrice")
            if priceObj is not None:
                price = priceObj['content']
            else:
                price = bsObj.find(text=re.compile('판매가')).parent.next_sibling.next_sibling.get_text()

            # meta 이용 끝

            # script 이용
            # 카테고리
            # dtmDataLayer = bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)')).get_text()
            dtmDataLayer = bsObj.find(text=re.compile('var dtmDataLayer= (.*?)'))
            # bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)'))는 Tag를 뱉고
            # bsObj.find(text=re.compile('var dtmDataLayer= (.*?)'))는 navigableString을 뱉는다
            category1Obj = re.search('(?<=product_category1: ").+?(?=\")', dtmDataLayer)

            if category1Obj is not None:
                category1 = category1Obj.group(0)
                category2 = re.search('(?<=product_category2: ").+?(?=\")', dtmDataLayer).group(0)
            else:
                # 에뛰드
                categoryObjList = bsObj.findAll('select', {'class':'htc13'})
                # categoryObjList = bsObj.findAll({'class': 'htc13'}) 로 찾으면 안 나옴
                categoryList = []
                for categoryObj in categoryObjList:
                    selectedCategory = categoryObj.find(selected='selected').get_text()
                    categoryList.append(selectedCategory)
                category1 = categoryList[0]
                category2 = categoryList[1]

            # script 이용 끝

            # 옵션명
            optionObjList = bsObj.findAll(name='input', attrs={'name': 'optionSelector'})
            options = ''
            for i in range(0, len(optionObjList)):
                option = optionObjList[i]['kindnm']
                options += option
                if i < len(optionObjList) - 1:
                    options += '\n'

            if len(options) == 0:
                # 에뛰드
                optionObj = bsObj.find(id='sapCdList1')
                options = ''
                if optionObj is not None:
                    optionObjList = optionObj.findAll('option', value=re.compile('[0-9]+'))
                    for i in range(0, len(optionObjList)):
                        option = optionObjList[i].get_text().replace('[품절]', '')
                        options += option
                        if i < len(optionObjList) - 1:
                            options += '\n'
                        # '\r\n' 붙이면 다 프린트되고 '\r'만 붙이면 마지막 라인만 출력
                        # \n is the *nix line break, while \r\n is the Windows line break... (Windows likes to be special...) For the most part, \n is what you need.

            # 출력
            product = dict()
            product['brand'] = brandText
            product['category1'] = category1
            product['category2'] = category2
            product['product'] = productName
            product['options'] = options
            product['price'] = price
            product['amount'] = amount
            product['ingredients'] = ingredients
            product['image'] = productImage
            product['url'] = internalLink

            print(brandText)
            print(category1)
            print(category2)
            print(productName)
            print(options)
            print(price)
            print(amount)
            print(ingredients)
            print(productImage)
            print(internalLink)

            writer.writerow(product)

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

        except AttributeError as e:
            print(e)
            print(internalLink)

# for elem in bsObj(text="전성분"):
#     # print(elem.parent.parent.next_sibling.child.get_text())
#     for child in elem.parent.parent.parent.children:
#         print(child)

# outFile = "/Users/jihyunson/PycharmProjects/crawlIngredients/url.txt"
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
