# hwahae-crawling
화장품 상품 정보 크롤링

특정 웹사이트에서 신제품 페이지에 있는 화장품 정보를 크롤링합니다.


Part1. 신제품 페이지 페이지 소스 다운 받기

현재 프로젝트 안에 있는 사이트는 에뛰드하우스, 이니스프리, 아모레퍼시픽몰이며 각기 신제품 페이지의 구성은 다릅니다.
 >> 1. 에뛰드하우스는 페이징처리가 되어 있어 셀레니움을 통해 각 페이지 버튼을 눌러 페이지소스를 다운 받습니다.
 >> 2. 아모레퍼시픽몰은 신제품 페이지가 따로 있는 것이 아니라 '신상'이라는 필터가 있어 셀레니움을 통해 해당 필터를 선택한 뒤 '신상'이 적용된 페이지가 로드되면 다운 받습니다.

Part2. 신제품 페이지 소스에서 제품 상세 링크 크롤링하기
 >> 1. 기존 csv 파일에 있는 제품을 다시 크롤링하지 않기 위해서 기존 csv 파일에서 'url' 칼럼에 있는 링크들을 리스트로 만듭니다.
 >> 2. part1에서 다운받은 페이지 소스에서 기존 파일에 없었던 url을 크롤링하여 리스트로 만듭니다.
 
Part3. 제품 상세 페이지에서 제품 정보 크롤링하기
 >> 1. 화장품이 아닌 제품은 pass 합니다.
      >> 1. 사용기한 element가 없는 경우
      >> 2. 사용기한 정보에 '공산품' 문구가 있는 경우
      >> 3. 사용기한 정보에 '제품 상세설명 참고'밖에 문구가 없는 경우
 >> 2. 브랜드 정보를 크롤링합니다.
 >> 3. 용량 정보를 크롤링합니다.
 >> 4. 옵션명 정보를 크롤링합니다.
 >> 5. 성분 정보를 크롤링합니다.
 >> 6. 제품 이미지 주소를 크롤링합니다.
 >> 7. 카테고리 정보를 크롤링합니다.
      
