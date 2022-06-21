import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
    'https://www.bbc.com/sport/football/teams',
    headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')
names = soup.select(
    'div > div > div.gel-layout__item.gel-2\/3\@l > article > div.qa-story-body.story-body.gel-pica.gel-10\/12\@m.gel-7\/8\@l.gs-u-ml0\@l.gs-u-pb\+\+ > table:nth-child(4) > tbody > tr'
)

for name in names:
    tmp_teamname = name.find_all('span')
    tmp_teambbc = name.find_all('a')
    for x in [0, 1, 2]:
        try:
            # team 이름
            team_name = tmp_teamname[x].text
            # print(team_name)
            # team BBC 사이트
            team_bbc = tmp_teambbc[x].get('href')
            # print(team_bbc)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
            data = requests.get(team_bbc, headers=headers)
            soup2 = BeautifulSoup(data.text, 'html.parser')
            logo = soup2.select(
                '#main-content > div:nth-child(1) > div.ssrcss-1hdgz05-TopicHeaderWrapper.e1mh12xb4 > div > div > div > div > span > img'
            )

            # team logo src 주소
            team_logo = str(logo[0]).split('src="')[1].split('"')[0]
            # print(team_logo)

            # 최근 경기 결과
            game_team = soup2.find_all(attrs={'class': 'eair9203'})
            game_score = soup2.find_all(attrs={'class': 'eair9202'})
            for x in [0]:
                blue_name = game_team[x].text
                blue_score = game_score[x].text
            for x in [1]:
                red_name = game_team[x].text
                red_score = game_score[x].text

            #print(blue_name, blue_score, ':', red_name, red_score)


        except:
            continue
