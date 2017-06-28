import re
import certifi
from urllib.request import urlopen
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def crawl_product(link, driver):
    print('>>>New Product Starts: ' + link)
    try:
        html_file = urlopen(link, cafile=certifi.where())
        bs_obj = BeautifulSoup(html_file, "html.parser")

        if bs_obj.find('th', text=re.compile('제조')) is None:
            driver.get(link)
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '제조')]")))
                # 더페이스샵 옵션 선택 개발 중
                # element = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//ul[@class='euiSelectList'/li[1]']")))
                # element.click()
                # pageSource = driver.page_source
            except TimeoutException:
                pass
            finally:
                page_source = driver.page_source
                bs_obj = BeautifulSoup(page_source, "html.parser")

        # 제품 요약 정보 이용
        # 솜 거르기
        # expirationObj = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간'))
        # expirationObj = bsObj.find("th", text=re.compile('제조연월/사용기간'))
        expiration_obj = bs_obj.find("th", text=re.compile('사용기한|사용기간'))
        if expiration_obj is None:
            print('>>>return: 사용기한이 없음-> 소품')
            return

        # 공산품 거르기
        # expiration = bsObj.find("th", text=re.compile('사용기한 또는 개봉 후 사용기간')).parent.td.get_text()
        expiration = bs_obj.find("th", text=re.compile('사용기한|사용기간')).parent.td.get_text()
        if "공산품" in expiration or len(expiration.strip()) == 0 or re.match('^[\s]*제품 상세설명 참고[\s]*$', expiration) is not None:
            print('>>>return: 공산품')
            return

        # 브랜드
        # brand = bsObj.find("th", text=re.compile('제조자/제조판매원')).parent.td.get_text()
        # 에뛰드 제조사 / 제조국 / 판매원
        # 제조자/ 제조판매업자/ 제조국 다 다른 라인
        brand_obj = bs_obj.find("th", text=re.compile('제조.*판매'))
        if brand_obj is not None:
            brand = brand_obj.parent.td.get_text()
            brand_text_list = brand.split("/")
            brand_text = brand_text_list[-1]  # 제조판매원은 보통 맨 마지막에 위치한다
        else:
            brand_obj = bs_obj.find("th", text=re.compile('제조사|제조자'))
            brand = brand_obj.parent.td.get_text()
            brand_text_list = brand.split("/")
            brand_text = brand_text_list[0]  # 제조판매원이 안 나온 경우 제조사가 보통 제조국보다 먼저 위치한다
        brand_text = brand_text.replace("(주)", "")
        brand_text = brand_text.replace("㈜", "").strip()

        if brand_text == '아모레퍼시픽' and bs_obj.find(True, text=re.compile('전성분 정보')) is not None:
            brand_text = bs_obj.find(True, text=re.compile('전성분 정보')).parent.parent.find(
                attrs={'class': 'brandNm'}).get_text()
        print(brand_text)

        # 용량
        amount = bs_obj.find("th", text=re.compile("용량")).parent.td.get_text().strip()
        print(amount)

        # 옵션명
        option_obj_list = bs_obj.findAll(name='input', attrs={'name': 'optionSelector'})
        options = ''
        for i in range(0, len(option_obj_list)):
            option = option_obj_list[i]['kindnm']
            options += option
            if i < len(option_obj_list) - 1:
                options += '\n'

        if len(options) == 0:
            # 에뛰드
            option_obj = bs_obj.find(id='sapCdList1')
            options = ''
            if option_obj is not None:
                option_obj_list = option_obj.findAll('option', value=re.compile('[0-9]+'))
                for i in range(0, len(option_obj_list)):
                    option = option_obj_list[i].get_text().replace('[품절]', '')
                    options += option
                    if i < len(option_obj_list) - 1:
                        options += '\n'

        # 성분
        # 이니스프리
        ingredients_obj = bs_obj.find("p", text=re.compile('전성분 보기'))
        if ingredients_obj is not None and ingredients_obj.next_sibling.next_sibling is not None:
            ingredients = ingredients_obj.next_sibling.next_sibling.get_text().strip()
        # 에뛰드
        elif bs_obj.find(alt=re.compile('전성분$')) is not None:
            ingredients = bs_obj.find(alt=re.compile('전성분$')).parent.parent.get_text().strip()
        # 아모레 퍼시픽 몰
        elif bs_obj.find(True, text=re.compile('전성분 정보')) is not None:
            ingredients_objs = bs_obj.find(True, text=re.compile('전성분 정보')).parent.parent.find_all('p')
            ingredients = ''
            options = ''

            for ingredients_obj in ingredients_objs:
                option_obj = ingredients_obj.parent.find(attrs={'class': 'option'})
                ingredient = ingredients_obj.get_text()
                # 치약
                if '주성분' in ingredient:
                    print('>>>return: 치약이므로 넘김')
                    return
                # \r\n -> ,   \r\n이 반복되고 \s(빈 문자)가 아닌 문자가 따라오는 경우 ', '로 바꾼다 '정제수\r\n\r\n디메치콘'-> '정제수, 디메치콘'
                ingredient = re.sub('(\\r|\\n)+(?=[^\s])', ', ', ingredient)
                # 콤마가 있으면서 빈칸이 많았던 경우에는 ',\r\n' 콤마가 두 개가 된다 ',, '
                ingredient = ingredient.replace(',,', ',')
                if not ingredient.endswith('\n'):
                    ingredient += '\n'  # 옵션 간의 줄나눔.

                if ingredient == '아직 등록된 전성분이 없습니다.\n':
                    # 성분에 추가하지 않고 다음 옵션으로
                    continue

                if option_obj is not None:
                    ingredients += option_obj.get_text() + '\n'
                    options += option_obj.get_text() + '\n'

                ingredients += ingredient

            if ingredients == '':
                print('>>>return: 소품 or 모든 옵션에 전성분이 등록 안 된 경우')
                return
        # 더페이스샵 전성분보기 버튼 없음
        elif bs_obj.find('th', text='주요성분') is not None:
            ingredients = bs_obj.find('th', text='주요성분').parent.td.get_text()
        print(options)
        print(ingredients)

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

        # 이니스프리, 아모레퍼시픽
        product_name_obj = bs_obj.find(property="rb:itemName")
        if product_name_obj is not None:
            product_name = product_name_obj['content'].strip()
        # 더페이스샵
        elif bs_obj.find(property="og:title") is not None:
            product_name = bs_obj.find(property="og:title")['content'].strip()
        else:
            # 에뛰드
            product_name_string = bs_obj.title.get_text()
            product_name_list = product_name_string.split("-")
            product_name = product_name_list[-1]
        print(product_name)

        # 제품 이미지
        if bs_obj.find('img', alt=re.compile('확대이미지')) is not None:
            image = bs_obj.find('img', alt=re.compile('확대이미지'))['src']
        elif bs_obj.find(property=re.compile('itemImage', flags=re.IGNORECASE)) is not None:
            image = bs_obj.find(property=re.compile('itemImage', flags=re.IGNORECASE))['content']
        else:
            image = bs_obj.find(property=re.compile('image', flags=re.IGNORECASE))['content']
        print(image)

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
        price_obj = bs_obj.find(property="rb:originalPrice")
        if price_obj is not None:
            price = price_obj['content']
        else:
            # 에뛰드
            # price = bsObj.find(text=re.compile('판매가')).parent.next_sibling.next_sibling.get_text()
            # priceObj = bsObj.find(re.compile('t'), text=re.compile('판매가'))
            # priceObjParent = bsObj.find(text=re.compile('판매가')).parent
            price_obj_parent_next_sibling = bs_obj.find(text=re.compile('판매가')).parent.next_sibling
            if price_obj_parent_next_sibling is not None:
                price = price_obj_parent_next_sibling.next_sibling.get_text()
            else:
                price = bs_obj.find(re.compile('t'), text=re.compile('판매가')).next_sibling.next_sibling.get_text()

        price = price.replace('원', '')
        price = price.replace(',', '')
        price = price.replace('쿠폰', '')
        price = price.replace('다운', '')
        price = price.replace('\n', '')
        print(price)
        # meta 이용 끝

        # script 이용
        # 카테고리
        category1 = ''
        category2 = ''
        # dtm_data_layer = bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)')).get_text()
        dtm_data_layer = bs_obj.find(text=re.compile('var dtmDataLayer= (.*?)'))
        # bsObj.find("script", text=re.compile('var dtmDataLayer= (.*?)'))는 Tag를 뱉고
        # bsObj.find(text=re.compile('var dtmDataLayer= (.*?)'))는 navigableString을 뱉는다
        if dtm_data_layer is not None:
            category1_obj = re.search('(?<=product_category1: ").+?(?=\")', dtm_data_layer)

            if category1_obj is not None:
                category1 = category1_obj.group(0)
                category2 = re.search('(?<=product_category2: ").+?(?=\")', dtm_data_layer).group(0)
            else:
                # 에뛰드
                category_obj_list = bs_obj.findAll('select', {'class': 'htc13'})
                # category_obj_list = bsObj.findAll({'class': 'htc13'}) 로 찾으면 안 나옴
                category_list = []
                for categoryObj in category_obj_list:
                    selected_category = categoryObj.find(selected='selected').get_text()
                    category_list.append(selected_category)
                category1 = category_list[0]
                category2 = category_list[1]
        elif bs_obj.find(property=re.compile('category1')) is not None:
            category1 = bs_obj.find(property=re.compile('category1'))['content']
            category1 = bs_obj.find(href=re.compile(category1 + '$')).get_text()
            if bs_obj.find(property=re.compile('category2')) is not None:
                category2 = bs_obj.find(property=re.compile('category2'))['content']
                if bs_obj.find(href=re.compile(category2 + '$')) is not None:
                    category2 = bs_obj.find(href=re.compile(category2 + '$')).get_text()
                elif bs_obj.find(property=re.compile('category3')) is not None:
                    category3 = bs_obj.find(property=re.compile('category3'))['content']
                    category2 = bs_obj.find(href=re.compile(category3 + '$')).get_text()
        elif bs_obj.find(text=re.compile('.CATE_SEQ')) is not None:
            cate_obj = bs_obj.find(text=re.compile('.CATE_SEQ'))
            category2_obj = re.search('(?<=CATE_SEQ).+?(?=\;)', cate_obj)
            if category2_obj is not None:
                category2 = category2_obj.group(0)
                category2 = category2.replace(' ', '')
                category2 = category2.replace('=', '')
                category2 = category2.replace('"', '')
                category2 = category2.replace('\t', '')
                category1_obj = re.search('(?<=P_CATE_SEQ).+?(?=\;)', cate_obj)
                category1 = category1_obj.group(0)
                category1 = category1.replace(' ', '')
                category1 = category1.replace('=', '')
                category1 = category1.replace('"', '')
                category1 = category1.replace('\t', '')
                category1 = bs_obj.find(href=re.compile('=' + category1 + '$'), text=re.compile('.*')).get_text()
                category2 = bs_obj.find(href=re.compile('=' + category2 + '$'), text=re.compile('.*')).get_text()
        print(category1)
        print(category2)
        # script 이용 끝

        product = dict()
        product['brand'] = brand_text
        product['category1'] = category1
        product['category2'] = category2
        product['product'] = product_name
        product['options'] = options
        product['price'] = price
        product['amount'] = amount
        product['ingredients'] = ingredients
        product['image'] = image
        product['url'] = link

        return product

    except AttributeError as e:
        print('error occurred: ' + e)
        print(link)
