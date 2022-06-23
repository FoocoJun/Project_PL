import requests
from bs4 import BeautifulSoup

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
# data = requests.get(
#     'https://www.bbc.com/sport/football/teams',
#     headers=headers)
# soup = BeautifulSoup(data.text, 'html.parser')
# names = soup.select(
#     'div > div > div.gel-layout__item.gel-2\/3\@l > article > div.qa-story-body.story-body.gel-pica.gel-10\/12\@m.gel-7\/8\@l.gs-u-ml0\@l.gs-u-pb\+\+ > table:nth-child(4) > tbody > tr'
# )
#
# for name in names:
#     tmp_teamname = name.find_all('span')
#     tmp_teambbc = name.find_all('a')
#     for x in [0, 1, 2]:
#         try:
#             ## team 이름
#             team_name = tmp_teamname[x].text
#             # print(team_name)
#             ## team BBC 사이트
#             team_bbc = tmp_teambbc[x].get('href')
#             # print(team_bbc)
#
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
#             data = requests.get(team_bbc, headers=headers)
#             soup3 = BeautifulSoup(data.text, 'html.parser')
#             logo = soup3.select(
#                 '#main-content > div:nth-child(1) > div.ssrcss-1hdgz05-TopicHeaderWrapper.e1mh12xb4 > div > div > div > div > span > img'
#             )
#
#             ## team logo src 주소
#             # team_logo = str(logo[0]).split('src="')[1].split('"')[0]
#             # print(team_logo)
#
#             ## 최근 경기 결과 / 다음 경기 정보
#             # game_team = soup3.find_all(attrs={'class': 'eair9203'})
#             # game_score = soup3.find_all(attrs={'class': 'eair9202'})
#             # plan_schedule = soup3.find_all(attrs={'class': 'eo2yrsf2'})
#             team_news = soup3.find_all(attrs={'class': 'e6wdqbx0','class':'e14e9ror0'})
#             print(team_news)
#
#
#             ## 업데이트 소요에 따라 for 구문 남겨둠
#             # for x in [0]:
#             #     blue_name = game_team[x].text
#             #     blue_score = game_score[x].text
#             # for x in [1]:
#             #     red_name = game_team[x].text
#             #     red_score = game_score[x].text
#             # for x in [2]:
#             #     plan_blue_name = game_team[x].text
#             # for x in [3]:
#             #     plan_red_name = game_team[x].text
#             # for x in [0]:
#             #     plan_game_time = plan_schedule[x].text
#             #     plan_time = plan_schedule[x].text.split('at')[1].split('on')[0]
#             #     plan_day = plan_schedule[x].text.split('on')[1][0:3]
#             #     plan_date = plan_schedule[x].text.split('on')[1].split(' ')[0][6:]
#             #     plan_month = plan_schedule[x].text.split('on')[1].split('of')[1]
#             #     print(plan_time,plan_day,plan_date,plan_month)
#             #
#             # print('최근 경기:', blue_name, blue_score, ':', red_name, red_score)
#             # print('다음 경기:', plan_blue_name, ':', plan_red_name)
#             # print('날짜:', plan_month, plan_date, plan_day, plan_time)
#
#
#         except:
#             continue

### 뉴스 크롤링

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
# 테스트 시 'https://www.bbc.com/sport/football/teams/afc-bournemouth' 이용
data = requests.get(team_bbc, headers=headers)
soup3 = BeautifulSoup(data.text, 'html.parser')
# 뉴스 요약(첫문단,사진) 크롤링
tmp = soup3.select(
    '#main-content > div:nth-child(1) > div.ssrcss-1ocoo3l-Wrap.e42f8511 > div.ssrcss-gfrs6h-StackWrapper.e1d6xluq1 > ol > li')

# 뉴스 제목 및 게시일 크롤링
team_news = soup3.find_all(attrs={'class': 'e6wdqbx0', 'class': 'e14e9ror0'})

# 카운트 및 dict 선언
count = 0
news_dict = {}

for x in team_news:
    count = count + 1
    # 제목이 게시일이랑 붙어있어서 찢는 과정
    news_title = x.text[:x.text.find('published at ')]
    news_date = x.text[x.text.find('published at '):]
    news_dict[count] = [news_title, news_date]

# 카운트 초기화
count = 0

for y in tmp:
    # 글이 p tag로 이루어진 경우
    if y.select_one('article > p'):
        news_summ = y.select_one('article > p').text
        count = count + 1
        news_dict[count].append(news_summ)
    # 글이 li tag로 이루어진 경우
    elif y.select_one('article > ul > li'):
        news_summ = y.select_one('p').text
        count = count + 1
        news_dict[count].append(news_summ)

    # 글이 img tag로 이루어진 경우
    elif y.select_one('article > figure > div > span > img'):
        news_summ = y.select_one('article > figure > div > span > img').get('src')
        count = count + 1
        news_dict[count].append(news_summ)
    else:
        continue

print(news_dict)
