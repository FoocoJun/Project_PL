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
def home():
    return render_template('index.html')

@app.route('/team')
def team_site():
    return render_template('team.html')


# 팀 사이트 랜더링
@app.route('/team/<teamtitle>')
def team_temp(teamtitle):
    # 필요 자료형으로 치환 ('-' 제거 등)
    teamtitle = str(teamtitle).replace('-', ' ')
    # 팀에 관한 db 불러오기
    team = db.teams.find_one({'name': teamtitle})

    # 팀 경기결과 불러오기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(team['bbc'], headers=headers)
    soup2 = BeautifulSoup(data.text, 'html.parser')

    # 최근 경기 결과 / 다음 경기 정보
    game_team = soup2.find_all(attrs={'class': 'eair9203'})
    game_score = soup2.find_all(attrs={'class': 'eair9202'})
    plan_schedule = soup2.find_all(attrs={'class': 'eo2yrsf2'})
    # 업데이트 소요에 따라 for 구문 남겨둠
    for x in [0]:
        blue_name = game_team[x].text
        blue_score = game_score[x].text
    for x in [1]:
        red_name = game_team[x].text
        red_score = game_score[x].text
    for x in [2]:
        plan_blue_name = game_team[x].text
    for x in [3]:
        plan_red_name = game_team[x].text
    for x in [0, 1, 2, 3]:
        plan_time = plan_schedule[x].text.split('at')[1].split('on')[0]
        plan_day = plan_schedule[x].text.split('on')[1][0:3]
        plan_date = plan_schedule[x].text.split('on')[1].split(' ')[0][6:]
        plan_month = plan_schedule[x].text.split('on')[1].split('of')[1]

    # print('최근 경기:',blue_name, blue_score, ':', red_name, red_score)
    # print('다음 경기:',plan_blue_name,':',plan_red_name)
    # print('날짜:',plan_month,plan_date,plan_day,plan_time)

    return render_template('teamTemp.html',
                           teamtitle=teamtitle,
                           teamlogo=team['logo'],
                           teamname=team['name'],
                           teambbc=team['bbc'],
                           # 최근 경기 결과
                           blue_name=blue_name,
                           blue_score=blue_score,
                           red_name=red_name,
                           red_score=red_score,
                           # 다음 경기 계획
                           plan_blue_name=plan_blue_name,
                           plan_red_name=plan_red_name,
                           plan_month=plan_month,
                           plan_date=plan_date,
                           plan_day=plan_day,
                           plan_time=plan_time,
                           )


# admin /시즌 말 팀 목록 초기화 크롤링
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

                doc = {'name': team_name,
                       'logo': team_logo,
                       'insta': '',
                       'fb': '',
                       'official': '',
                       'bbc': team_bbc,
                       'namu': ''}
                db.teams.update_one(doc)
            except:
                continue
    return jsonify({'msg': '팀목록 새로고침 완료'})


@app.route("/team/<teamtitle>/write", methods=["POST"])
def ariticle_post():
    #글쓰기 기능 구현
    article_receive = request.form['article_give']
    date_receive = request.form['date_give']

    all_article = list(db.articles.find({}, {'_id': False}))
    count = len(all_article) + 1

    doc = {
        'num': count,
        'article': article_receive,
        'date': date_receive,
        'like': 0,
        'liked': [],
        'disliked': []
    }

    db.articles.insert_one(doc)

    return jsonify({'msg': '등록되었습니다.'})


# 좋아요 싫어요 라디오 버튼식 구현
@app.route("/team/<teamtitle>/write/likes", methods=["POST"])
def article_like():
    number_receive = request.form['number_give']
    # 로그인 구현 전 닉네임 예시
    userNickname = 'GICK'

    # 게시글 번호(number_receive)에 따른 좋아요 명단
    isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
    # 게시글 번호(number_receive)에 따른 싫어요 명단
    isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']

    if isdisliked.count(userNickname) == 0:  # 싫어요 명단에 이름(userNickname)이 없고
        if isliked.count(userNickname) == 0:  # 좋아요 명단에 이름(userNickname)이 없으면
            # 좋아요 명단에 이름(userNickname) push
            db.articles.update_one({'num': int(number_receive)}, {'$push': {'liked': userNickname}})
            # 좋아요 명단(liked) 다시 불러오기
            isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
            # 좋아요 수(like) = 좋아요 명단-싫어요 명단
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '좋아요를 했습니다.'})

        elif isliked.count(userNickname) == 1:  # 좋아요 명단에 이름이 있으면
            # 좋아요 명단에서 이름(userNickname) pull
            db.articles.update_one({'num': int(number_receive)}, {'$pull': {'liked': userNickname}})
            isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '좋아요를 취소했습니다.'})

    elif isdisliked.count(userNickname) == 1:  # 싫어요 명단에 이름(userNickname)이 있고
        if isliked.count(userNickname) == 0:  # 좋아요 명단에 이름(userNickname)이 없으면
            # 싫어요 명단에서 이름(userNickname) pull
            db.articles.update_one({'num': int(number_receive)}, {'$pull': {'disliked': userNickname}})

            # 좋아요 명단에 이름(userNickname) push
            db.articles.update_one({'num': int(number_receive)}, {'$push': {'liked': userNickname}})
            isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
            isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '좋아요를 했습니다.'})


@app.route("/team/<teamtitle>/write/dislikes", methods=["POST"])
def article_dislike():
    # 로그인 구현 전 닉네임 예시
    userNickname = 'GICK'

    number_receive = request.form['number_give']
    isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
    isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
    print(isdisliked)

    if isliked.count(userNickname) == 0:  # 좋아요 명단에 이름(userNickname)이 없고
        if isdisliked.count(userNickname) == 0:  # 싫어요 명단에 이름(userNickname)이 없으면
            db.articles.update_one({'num': int(number_receive)}, {'$push': {'disliked': userNickname}})
            isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '싫어요를 했습니다.'})
        elif isdisliked.count(userNickname) == 1:  # 싫어요 명단에 이름(userNickname)이 있으면
            db.articles.update_one({'num': int(number_receive)}, {'$pull': {'disliked': userNickname}})
            isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '싫어요를 취소했습니다.'})

    elif isliked.count(userNickname) == 1:  # 좋아요 명단에 이름(userNickname)이 있고
        if isdisliked.count(userNickname) == 0:  # 싫어요 명단에 이름이 없으면
            # 좋아요 명단에서 이름(userNickname) pull
            db.articles.update_one({'num': int(number_receive)}, {'$pull': {'liked': userNickname}})
            # 싫어요 명단에서 이름(userNickname) push
            db.articles.update_one({'num': int(number_receive)}, {'$push': {'disliked': userNickname}})
            isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
            isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '싫어요를 했습니다.'})


@app.route("/team/<teamtitle>/read", methods=["GET"])
def article_get():
    #게시판 내용 표시
    all_article = list(db.articles.find({}, {'_id': False}))
    all_users = list(db.users.find({}, {'_id': False}))
    return jsonify({'all_article': all_article, 'all_users': all_users})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
