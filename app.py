import requests
from bs4 import BeautifulSoup
import pyautogui

keyword = pyautogui.prompt("검색어를 입력하세요.")
lastpage = pyautogui.prompt("마지막 페이지번호를 입력해 주세요") #int 형으로 바꾼 부분을 원하는 페이지 숫자로 바꾸어 주면 됩니다. ex ) 3페이지까지는 30 , 100페이지까지는 100
pageNum = 1
for i in range(1, int(lastpage) * 10, 10): #range 의 결과로 30까지의 숫자만 보여준다(30을 수정하면 페이지는 수정가능 함)
    print(f"---------------------------------{pageNum}페이지입니다-----------------------------------") #사용하지 않아도 됨 (페이지를 구분지어주는 장치)
    response = requests.get(f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={keyword}&sort=1&photo=0&field=0&pd=0&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start={i}")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select(".news_tit") #결과는 리스트

    for link in links:
        title = link.text  # 태그 안에 텍스트요소를 가져온다
        url = link.attrs['href']  # herf의 속성값을 가져온다
        print(title, url)
    pageNum = pageNum + 1
