from flask import Flask, render_template, request, jsonify

app: Flask = Flask(__name__)

# pymongo 양식
from pymongo import MongoClient

client = MongoClient('mongodb+srv://HAJUN:9965@cluster0.oudgkww.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbfootball

# bs4 양식
import requests
from bs4 import BeautifulSoup


@app.route('/')
def team_site():
    return render_template('team.html')


@app.route('/team/<teamtitle>')
def team_temp(teamtitle):
    #필요 자료형으로 치환
    teamtitle = str(teamtitle).replace('-', ' ')
    team=db.teams.find_one({'name':teamtitle})

    return render_template('teamTemp.html',
                           teamtitle=teamtitle,
                           teamlogo=team['logo'],
                           teamname=team['name']
                           )










#admin /시즌 말 팀 목록 초기화 크롤링
@app.route("/admin/teamlist", methods=["GET"])
def teamlist_get():
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
                team_name = tmp_teamname[x].text.lower()
                print(team_name)
                # team BBC 사이트
                team_bbc = tmp_teambbc[x].get('href')
                print(team_bbc)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
                data = requests.get(team_bbc, headers=headers)
                soup2 = BeautifulSoup(data.text, 'html.parser')
                logo = soup2.select(
                    '#main-content > div:nth-child(1) > div.ssrcss-1hdgz05-TopicHeaderWrapper.e1mh12xb4 > div > div > div > div > span > img'
                )

                # team logo src 주소
                team_logo = str(logo[0]).split('src="')[1].split('"')[0]
                print(team_logo)

                doc ={'name': team_name,
                     'logo': team_logo,
                     'insta':'',
                     'fb':'',
                     'official':'',
                     'bbc': team_bbc,
                     'namu':''}
                db.teams.update_one(doc)
            except:
                continue
    return jsonify({'msg': '팀목록 새로고침 완료'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
