from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# bs4 양식
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
    'https://steamcommunity.com/profiles/76561198083882978/myworkshopfiles/?appid=0&sort=score&browsefilter=myfavorites&view=imagewall&p=1&numperpage=30',
    headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

modes = soup.select('#leftContents > div.workshopBrowseItems > div')

# pymongo 양식
from pymongo import MongoClient

client = MongoClient('mongodb+srv://HAJUN:9965@cluster0.oudgkww.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbfootball


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/team/write", methods=["POST"])
def ariticle_post():
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
@app.route("/team/write/likes", methods=["POST"])
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


@app.route("/team/write/dislikes", methods=["POST"])
def article_dislike():
    # 로그인 구현 전 닉네임 예시
    userNickname = 'GICK'

    number_receive = request.form['number_give']
    isliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['liked']
    isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
    print(isdisliked)

    if isliked.count(userNickname) == 0:    # 좋아요 명단에 이름(userNickname)이 없고
        if isdisliked.count(userNickname) == 0:    # 싫어요 명단에 이름(userNickname)이 없으면
            db.articles.update_one({'num': int(number_receive)}, {'$push': {'disliked': userNickname}})
            isdisliked = db.articles.find_one({'num': int(number_receive)}, {'_id': False})['disliked']
            db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': len(isliked) - len(isdisliked)}})
            return jsonify({'msg': '싫어요를 했습니다.'})
        elif isdisliked.count(userNickname) == 1:   # 싫어요 명단에 이름(userNickname)이 있으면
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


@app.route("/team/read", methods=["GET"])
def article_get():
    all_article = list(db.articles.find({}, {'_id': False}))
    all_users = list(db.users.find({}, {'_id': False}))
    return jsonify({'all_article': all_article, 'all_users': all_users})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
