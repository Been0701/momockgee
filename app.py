from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from search import search_keyword


app = Flask(__name__)
client = MongoClient('mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority')
db = client.momockgee

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"
SECRET_KEY = 'SPARTA'

# @app.route('/')
# def home():
#    return render_template("index.html")

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route("/search", methods=["POST"])
def post_search():
    product_receive = request.form["product_give"]
    results = search_keyword(product_receive)
    return jsonify({'search_results': results})

@app.route("/all_products", methods=["GET"])
def get_all_products():
    all_products_list = list(db.posting.find({},{'_id':False}))
    return jsonify({'all_products' : all_products_list})

@app.route("/comment", methods=["GET"])
def comment_get():
    comments_list = list(db.comment.find({},{'_id':False}))
    return jsonify({'msg':'GET 연결 완료!'})

@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    comment_list = list(db.comment.find({}, {'_id': False}))
    count = len(comment_list) + 1
    doc = {
        # 'num': count,
        'num': 0,
        'comment': comment_receive
    }
    db.comment.insert_one(doc)
    return jsonify({'msg': '등록 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)