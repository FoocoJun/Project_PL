
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import jwt
import hashlib

app: Flask = Flask(__name__)

# pymongo 양식
from pymongo import MongoClient

client = MongoClient('mongodb+srv://HAJUN:9965@cluster0.oudgkww.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbfootball

# bs4 양식
import requests
from bs4 import BeautifulSoup

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


@app.route('/')
def home():
    # 팀에 관한 db 불러오기
    all_teams = list(db.teams.find({}, {'_id': False}))

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info, all_teams=all_teams)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    # 팀에 관한 db 불러오기
    all_teams = list(db.teams.find({}, {'_id': False}))

    msg = request.args.get("msg")
    return render_template('login.html', msg=msg, all_teams=all_teams)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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
    if team:  # 주소가 올바른 팀 이름이면(데이터베이스에 있는 팀 이름이면!)
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
        ### 뉴스 크롤링

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        # 테스트 시 'https://www.bbc.com/sport/football/teams/afc-bournemouth' 이용
        data = requests.get(team['bbc'], headers=headers)
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
                               #뉴스 정보
                               # 팀 뉴스
                               news_dict=news_dict
                               )
    else:
        return jsonify({'msg': '올바르지 않은 접근방식입니다.'})


@app.route("/team/read", methods=["GET"])
def article_get():
    # 게시판 내용 표시
    all_articles = list(db.articles.find({}, {'_id': False}))
    all_users = list(db.users.find({}, {'_id': False}))
    return jsonify({'all_article': all_articles, 'all_users': all_users})


@app.route("/team/write", methods=["POST"])
def ariticle_post():
    # 쿠키에서 로그인 토큰을 받아온다.
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userNickname = payload['id']

        # 글쓰기 기능 구현
        article_receive = request.form['article_give']
        date_receive = request.form['date_give']
        team_receive = request.form['team_give']
        # print(team_receive)
        if not article_receive:
            return jsonify({'msg': '내용을 입력하세요.'})

        else:
            all_article = list(db.articles.find({}, {'_id': False}))
            count = len(all_article) + 1

            doc = {
                'num': count,
                'username': userNickname,
                'team': team_receive,
                'article': article_receive,
                'date': date_receive,
                'like': 0,
                'liked': [],
                'disliked': []
            }

            db.articles.insert_one(doc)
            return jsonify({'msg': '등록되었습니다.'})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'msg': "글 작성은 로그인을 해야합니다."})


# 좋아요 / 싫어요 라디오 버튼식 구현 (좋아요)
@app.route("/team/write/likes", methods=["POST"])
def article_like():
    # 쿠키에서 로그인 토큰을 받아온다.
    token_receive = request.cookies.get('mytoken')
    try:  # 로그인되어 있으면
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userNickname = payload['id']

        number_receive = request.form['number_give']

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
                return ('', 204)  # 브라우저에 아무런 응답도 하지 않는 방법

            elif isliked.count(userNickname) == 1:  # 좋아요 명단에 이름이 있으면
                # 좋아요 명단에서 이름(userNickname) pull
                db.articles.update_one({'num': int(number_receive)}, {'$pull': {'liked': userNickname}})
                isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
                db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
                return ('', 204)

        elif isdisliked.count(userNickname) == 1:  # 싫어요 명단에 이름(userNickname)이 있고
            if isliked.count(userNickname) == 0:  # 좋아요 명단에 이름(userNickname)이 없으면
                # 싫어요 명단에서 이름(userNickname) pull
                db.articles.update_one({'num': int(number_receive)}, {'$pull': {'disliked': userNickname}})

                # 좋아요 명단에 이름(userNickname) push
                db.articles.update_one({'num': int(number_receive)}, {'$push': {'liked': userNickname}})
                isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
                isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
                db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
                return jsonify('', 204)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'msg': "로그인을 해야합니다."})


# 좋아요 / 싫어요 라디오 버튼식 구현 (싫어요)
@app.route("/team/write/dislikes", methods=["POST"])
def article_dislike():
    token_receive = request.cookies.get('mytoken')
    try:  # 로그인되어 있으면
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userNickname = payload['id']

        number_receive = request.form['number_give']
        isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
        isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
        print(isdisliked)

        if isliked.count(userNickname) == 0:  # 좋아요 명단에 이름(userNickname)이 없고
            if isdisliked.count(userNickname) == 0:  # 싫어요 명단에 이름(userNickname)이 없으면
                db.articles.update_one({'num': int(number_receive)}, {'$push': {'disliked': userNickname}})
                isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
                db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
                return ('', 204)
            elif isdisliked.count(userNickname) == 1:  # 싫어요 명단에 이름(userNickname)이 있으면
                db.articles.update_one({'num': int(number_receive)}, {'$pull': {'disliked': userNickname}})
                isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
                db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
                return ('', 204)

        elif isliked.count(userNickname) == 1:  # 좋아요 명단에 이름(userNickname)이 있고
            if isdisliked.count(userNickname) == 0:  # 싫어요 명단에 이름이 없으면
                # 좋아요 명단에서 이름(userNickname) pull
                db.articles.update_one({'num': int(number_receive)}, {'$pull': {'liked': userNickname}})
                # 싫어요 명단에서 이름(userNickname) push
                db.articles.update_one({'num': int(number_receive)}, {'$push': {'disliked': userNickname}})
                isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
                isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
                db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
                return ('', 204)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'msg': "로그인을 해야합니다."})


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

