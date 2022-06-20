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
    #date_receive = request.form['date_give']

    all_article = list(db.articles.find({}, {'_id': False}))
    count = len(all_article) + 1

    doc = {
        'num': count,
        'article': article_receive,
        #'date': date_receive,
        'like': 0
    }

    db.articles.insert_one(doc)

    return jsonify({'msg': '등록되었습니다.'})

@app.route("/team/write/likes", methods=["POST"])
def article_like():

    #유저마다 likes 데이터베이스 따로 만들어서 두번 좋아요 안되게 + 내가 좋아한 글 구현

    number_receive = request.form['number_give']
    like = db.articles.find_one({'num': int(number_receive)})['like']
    db.articles.update_one({'num':int(number_receive)},{'$set':{'like':like+1}})
    return jsonify({'msg': '게시글에 좋아요를 눌렀습니다.'})

@app.route("/team/write/dislikes", methods=["POST"])
def article_dislike():
    number_receive = request.form['number_give']
    like = db.articles.find_one({'num': int(number_receive)})['like']
    db.articles.update_one({'num': int(number_receive)}, {'$set': {'like': like-1}})
    return jsonify({'msg': '게시글에 싫어요를 눌렀습니다.'})


@app.route("/team/read", methods=["GET"])
def article_get():
    all_article = list(db.articles.find({}, {'_id': False}))
    return jsonify({'all_article': all_article})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
