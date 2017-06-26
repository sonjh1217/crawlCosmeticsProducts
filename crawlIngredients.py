# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:55:48 2014

@author: user
"""
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
import re
import certifi
from bs4 import BeautifulSoup
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Retrieves a list of all Internal links found on a page
def getInternalLinks(bsObj, includeUrl, previousLinks=None):
    internalLinks = []
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

            if hrefValue not in internalLinks and (previousLinks is None or hrefValue not in previousLinks):
                internalLinks.append(hrefValue)
                print("internal link: " + hrefValue)

    if len(internalLinks) == 0:
        for link in bsObj.findAll("a", attrs={'class':'btn_detail'}):
            if link.attrs['id'] is not None:
                hrefValue = 'http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=' + link.attrs['id']
                if hrefValue not in internalLinks and (previousLinks is None or hrefValue not in previousLinks):
                    internalLinks.append(hrefValue)
                    print("internal link: " + hrefValue)

    return internalLinks

def getPageSourcesFrom(startingPageParam):
    pageSources = []
    # 보이지 않는 웹드라이버(팬텀)
    driver = webdriver.PhantomJS(executable_path='/Users/JihyunSon/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')
    # 첫 페이지를 로드한다. 첫 페이지 로드가 실패할 경우가 꽤 있어서, 30초로 타임아웃 설정하고 타임아웃 발생시 다시 로드 시도한다
    driver.set_page_load_timeout(30)
    while len(pageSources) == 0:
        try:
            driver.get(startingPageParam)

            # 신상을 체크한다. 아모레퍼시픽몰
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='label_AC006']")))
                element.click()
                try:
                    element = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "신상")]')))
                # 신상 클릭했는데 로드가 안 되는 것. 오류 상황임
                except TimeoutException:
                    driver.close()
                    print("신상 클릭했는데 로드가 안 됨. 오류 상황임")
                    return pageSources
            finally:
                currentPageNum = 1
                pageSource = driver.page_source
                pageSources.append(pageSource)
                print("currentPageNum: " + str(currentPageNum))
                while len(driver.find_elements(By.LINK_TEXT, str(currentPageNum + 1))) > 0:
                    try:
                        # 다음 페이지 버튼이 clickable해지는 순간을 기다린다. 10은 time-out을 의마한다
                        # 10초 동안 0.5초(default)마다 해당 element가 clickable한지 체크한다. 계속 못찾으면 throw TimeoutException
                        element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, str(currentPageNum + 1))))
                        # 다음 페이지 숫자를 가진 버튼이 있다면 계속한다
                        element.click()
                        currentPageNum += 1
                        print("currentPageNum: " + str(currentPageNum))
                        try:
                            # 다음 페이지가 로드되기를 기다린다 2 페이지일 경우 텍스트가 2인 strong 태그가 있다
                            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.XPATH, "//strong[text()=" + str(currentPageNum) + "]")))
                            # 로드 완료
                            pageSource = driver.page_source
                            pageSources.append(pageSource)
                        # 누르긴 했는데 로드가 실패함. 에러 상황임
                        except TimeoutException:
                            driver.quit()
                            print("clicked next page, and failed to load")
                            return pageSources
                    # 다음 페이지 버튼이 없는 경우. while에서 다음 페이지 요소를 체크하고 돌리기 때문에 일어나기 어려움
                    except TimeoutException:
                        # 드라이버 종료
                        driver.quit()
                        print("failed to find clickable next page link")
                        return pageSources
        except TimeoutException:
            continue
    driver.quit()
    return pageSources

# 제품 상세 링크 긁어오기
# csv 파일에 저장된 데이터 읽기
outFile = "test.csv"
try:
    with open(outFile, "r") as csvFile:
        reader = csv.DictReader(csvFile)
        previousLinks = list()
        for row in reader:
            previousLinks.append(row['url'])
except FileNotFoundError:
    previousLinks = None
    with open(outFile, "w") as csvFile:
        fieldnames = ['time', 'brand', 'category1', 'category2', 'product', 'options', 'price', 'amount', 'ingredients',
                      'image', 'url']
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        writer.writeheader()

# pageSources = []
startingPages = ["http://www.etude.co.kr/product.do?method=new", "http://www.innisfree.com/kr/ko/ShopNewPrdList.do", "http://www.amorepacificmall.com/shop/prod/shop_prod_product_list.do"]
# startingPages = ["http://www.etude.co.kr/product.do?method=new"]
internalLinks = []
for startingPage in startingPages:
    print("starting page: " + startingPage)
    # pageSources.extend(getPageSourcesFrom(startingPage))
    pageSources = getPageSourcesFrom(startingPage)
    domain = urlparse(startingPage).scheme + "://" + urlparse(startingPage).netloc
    for pageSource in pageSources:
        bsObj = BeautifulSoup(pageSource, "html.parser")
        internalLinks.extend(getInternalLinks(bsObj, domain, previousLinks=previousLinks))

# 카테고리
# startingPage = "http://www.innisfree.com/kr/ko/Product.do?catCd01=UA"

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

# 아모레퍼시픽몰
# internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170529000029791"]

#삭품: 사용기한에서 걸러짐
# internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170531000029873"]

#category2가 기능관련인 경우
# internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170523000029610"]

# 옵션 상품
# internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170526000029748"]

# 상품 정보 가져오기
with open('test.csv', mode='a') as csvfile:
    fieldnames = ['time','brand', 'category1', 'category2', 'product', 'options', 'price', 'amount', 'ingredients', 'image', 'url']
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # 'a' mode로 열면 reader 작동 안함

    for internalLink in internalLinks:
        try:
            htmlFile = urlopen(internalLink, cafile=certifi.where())
            bsObj = BeautifulSoup(htmlFile, "html.parser")

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

            if brandText == '아모레퍼시픽' and bsObj.find(True, text=re.compile('전성분 정보')) is not None:
                brandText = bsObj.find(True, text=re.compile('전성분 정보')).parent.parent.find(attrs={'class':'brandNm'}).get_text()
                # 왜 div를 넣으면 잘 찾고 안 넣으면 None이 나오냐? -> parameter가 name인 줄 알아서 그런다

            # 용량
            amount = bsObj.find("th", text=re.compile("용량")).parent.td.get_text().strip()

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

            # 성분
            # 이니스프리
            ingredientsObj = bsObj.find("p", text=re.compile('전성분 보기'))
            if ingredientsObj is not None and ingredientsObj.next_sibling.next_sibling is not None:
                ingredients = ingredientsObj.next_sibling.next_sibling.get_text().strip()
                # # '\r'이 있으면 마지막 라인만 프린트됨
                # ingredients = ingredients.replace("\r", "")
            # 에뛰드
            elif bsObj.find(alt=re.compile('전성분$')) is not None:
                ingredients = bsObj.find(alt=re.compile('전성분$')).parent.parent.get_text().strip()
            # 아모레 퍼시픽 몰
            elif bsObj.find(True, text=re.compile('전성분 정보')) is not None:
                # ingredients = bsObj.find(True, text=re.compile('전성분 정보')).parent.parent.find('p').get_text()
                ingredientsObjs = bsObj.find(True, text=re.compile('전성분 정보')).parent.parent.find_all('p')
                ingredients = ''
                options = ''

                for ingredientsObj in ingredientsObjs:
                    optionObj = ingredientsObj.parent.find(attrs={'class': 'option'})
                    if optionObj is not None:
                        ingredients += optionObj.get_text() + '\n'
                        options += optionObj.get_text() + '\n'
                    ingredients += ingredientsObj.get_text() + '\n'

                if ingredients == '아직 등록된 전성분이 없습니다.\n': #소품 등의 경우다
                    continue


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
            if bsObj.find(property=re.compile('itemImage', flags=re.IGNORECASE)) is not None:
                productImage = bsObj.find(property=re.compile('itemImage', flags=re.IGNORECASE))['content']
            else:
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

            price = price.replace('원', '')
            price = price.replace(',', '')

            # meta 이용 끝

            # script 이용
            # 카테고리
            category1 = ''
            category2 = ''
            # dtmDataLayer = bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)')).get_text()
            dtmDataLayer = bsObj.find(text=re.compile('var dtmDataLayer= (.*?)'))
            # bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)'))는 Tag를 뱉고
            # bsObj.find(text=re.compile('var dtmDataLayer= (.*?)'))는 navigableString을 뱉는다
            if dtmDataLayer is not None:
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
            elif bsObj.find(property=re.compile('category1')) is not None:
                category1 = bsObj.find(property=re.compile('category1'))['content']
                category1 = bsObj.find(href=re.compile(category1 + '$')).get_text()
                if bsObj.find(property=re.compile('category2')) is not None:
                    category2 = bsObj.find(property=re.compile('category2'))['content']
                    if bsObj.find(href=re.compile(category2 + '$')) is not None:
                        category2 = bsObj.find(href=re.compile(category2 + '$')).get_text()
                    elif bsObj.find(property=re.compile('category3')) is not None:
                        category3 = bsObj.find(property=re.compile('category3'))['content']
                        category2 = bsObj.find(href=re.compile(category3 + '$')).get_text()

            # script 이용 끝

            # 출력
            product = dict()
            product['time'] = currentTime
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

        except AttributeError as e:
            print(e)
            print(internalLink)

        except HTTPError as e:
            print(e)
            print(internalLink)
