from links import get_page_sources, get_links
from product import crawl_product

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from selenium import webdriver

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

startingPages = ["http://www.etude.co.kr/product.do?method=new", "http://www.innisfree.com/kr/ko/ShopNewPrdList.do", "http://www.amorepacificmall.com/shop/prod/shop_prod_product_list.do"]
internalLinks = []
try:
    driver = webdriver.Chrome(executable_path='/Users/JihyunSon/Documents/chromedriver')
    driver.set_page_load_timeout(30)
    for startingPage in startingPages:
        print("starting page: " + startingPage)
        # pageSources.extend(getPageSourcesFrom(startingPage))
        pageSources = get_page_sources(startingPage, driver)
        domain = urlparse(startingPage).scheme + "://" + urlparse(startingPage).netloc
        for pageSource in pageSources:
            bsObj = BeautifulSoup(pageSource, "html.parser")
            internalLinks.extend(get_links(bsObj, domain, previous_links=previousLinks))

    #제품 정보 긁어오기
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

    # 아모레퍼시픽몰 옵션
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=P00001221"]
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=000025659"]

    # 삭품: 사용기한에서 걸러짐
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170531000029873"]

    # category2가 기능관련인 경우
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170523000029610"]

    # 아모레퍼시픽몰 옵션 상품
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170526000029748"]

    # 아모레퍼시픽몰 옵션 없는 상품
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170620000030275"]

    # 아모레퍼시픽몰 치약
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=P00005067"]

    # 아모레퍼시픽몰 청결
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=P00004585"]

    # 아모레퍼시픽 옵션 성분 다 등록 안 됨
    # internalLinks = ["http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20160801000022128"]

    # 아모레퍼시픽 솜
    # internalLinks = [
    #     "http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=P00003618"]

    # 이니스프리 에뛰드 아모레퍼시픽
    # internalLinks = ["http://www.innisfree.com/kr/ko/ProductView.do?prdSeq=13438", "http://www.etude.co.kr/product.do?method=view&prdCd=101004084", "http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170526000029748"]
    # internalLinks = ["http://www.etude.co.kr/product.do?method=view&prdCd=101004084", "http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=SPR20170526000029748"]

    # 더페이스샵
    # internalLinks = ["http://www.thefaceshop.com/mall/product/product-view.jsp?dpid=AF006830"]

    # 더페이스샵 옵션
    # internalLinks = ["http://www.thefaceshop.com/mall/product/product-view.jsp?dpid=AF006548"]
    with open('test.csv', mode='a') as newProductsCSVFile:
        fieldnames = ['time','brand', 'category1', 'category2', 'product', 'options', 'price', 'amount', 'ingredients', 'image', 'url']
        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
        writer = csv.DictWriter(newProductsCSVFile, fieldnames=fieldnames)
        # 'a' mode로 열면 reader 작동 안함
        # driver = webdriver.PhantomJS(executable_path='/Users/JihyunSon/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')

        for internalLink in internalLinks:
            product = crawl_product(internalLink, driver)
            # 화장품 아닐 경우 넘어감
            if product is not None:
                product['time'] = currentTime
                writer.writerow(product)
finally:
    driver.quit()
