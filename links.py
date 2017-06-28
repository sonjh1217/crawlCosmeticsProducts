import re
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_page_sources(starting_page, driver):
    page_sources = []

    while len(page_sources) == 0:
        try:
            driver.get(starting_page)

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
                    return page_sources
            # 신상 버튼이 없는 경우
            except TimeoutException:
                pass
            # 팝업이 떠 있는 경우
            except WebDriverException:
                pop_close = driver.find_element(By.CLASS_NAME, 'pop_close')
                pop_close.click()

            finally:
                current_page_num = 1
                page_source = driver.page_source
                page_sources.append(page_source)
                print("currentPageNum: " + str(current_page_num))
                while len(driver.find_elements(By.LINK_TEXT, str(current_page_num + 1))) > 0:
                    try:
                        # 다음 페이지 버튼이 clickable 해지는 순간을 기다린다. 10은 time-out 을 의마한다
                        # 10초 동안 0.5초(default)마다 해당 element 가 clickable 한지 체크한다. 계속 못찾으면 throw TimeoutException
                        element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, str(current_page_num + 1))))
                        # 다음 페이지 숫자를 가진 버튼이 있다면 계속한다
                        element.click()
                        current_page_num += 1
                        print("currentPageNum: " + str(current_page_num))
                        try:
                            # 다음 페이지가 로드되기를 기다린다 2 페이지일 경우 텍스트가 2인 strong 태그가 있다
                            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.XPATH, "//strong[text()=" + str(current_page_num) + "]")))
                            # 로드 완료
                            page_source = driver.page_source
                            page_sources.append(page_source)
                        # 누르긴 했는데 로드가 실패함. 에러 상황임
                        except TimeoutException:
                            print("clicked next page, and failed to load")
                            return page_sources
                    # 다음 페이지 버튼이 없는 경우. while 에서 다음 페이지 요소를 체크하고 돌리기 때문에 일어나기 어려움
                    except TimeoutException:
                        print("failed to find clickable next page link")
                        return page_sources
        except TimeoutException:
            continue
    return page_sources


# Retrieves a list of all product detail links found on a page
def get_links(bs_obj, include_url, previous_links=None):
    links = []
    include_url = urlparse(include_url).scheme + "://" + urlparse(include_url).netloc
    for link in bs_obj.findAll("a", href=re.compile("[^a-z]productView.+", flags=re.IGNORECASE)):
        if link.attrs['href'] is not None:
            if link.attrs['href'].startswith("/"):
                href = include_url + link.attrs['href']
            elif link.attrs['href'].startswith('javascript'):
                href = link.attrs['href'].replace("javascript:productView('",
                                                       'http://www.etude.co.kr/product.do?method=view&prdCd=').replace(
                    "');", '')
            else:
                href = link.attrs['href']

            if href not in links and (previous_links is None or href not in previous_links):
                links.append(href)
                print("internal link: " + href)

    if len(links) == 0:
        for link in bs_obj.findAll("a", attrs={'class': 'btn_detail'}):
            if link.attrs['id'] is not None:
                href = 'http://www.amorepacificmall.com/shop/prod/shop_prod_product_view.do?i_sProductcd=' + \
                            link.attrs['id']
                if href not in links and (previous_links is None or href not in previous_links):
                    links.append(href)
                    print("internal link: " + href)

    return links
