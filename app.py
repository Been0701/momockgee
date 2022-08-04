from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from datetime import datetime, timedelta
from search import search_keyword
import os.path
from post_id import create_post_id

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# client = MongoClient("mongodb+srv://test:sparta@cluster0.mndqybx.mongodb.net/Cluster0?retryWrites=true&w=majority")
client = MongoClient('mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority')
db = client.momockgee

upload_forder = './static/upload'
if not os.path.exists(upload_forder):
    os.makedirs(upload_forder)

# @app.route('/')
# def home():
#     msg = request.args.get("msg")
#     return render_template('login.html', msg=msg)
#
#
# @app.route('/login')
# def login():
#     return render_template('index.html')
#
#
# @app.route('/sign_in', methods=['POST'])
# def sign_in():
#     # 로그인
#     username_receive = request.form['username_give']
#     password_receive = request.form['password_give']
#     pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
#     result = db.users.find_one({'username': username_receive, 'password': pw_hash})
#     if result is not None:
#         payload = {
#          'id': username_receive,
#          'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
#         }
#         token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
#         return jsonify({'result': 'success', 'token': token})
#     # 찾지 못하면
#     else:
#         return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
#
# @app.route('/sign_up/save', methods=['POST'])
# def sign_up():
#     username_receive = request.form['username_give']
#     password_receive = request.form['password_give']
#     password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
#     doc = {
#         "username": username_receive,                               # 아이디
#         "password": password_hash,                                  # 비밀번호
#         "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
#     }
#     db.users.insert_one(doc)
#     return jsonify({'result': 'success'})
#
# @app.route('/sign_up/check_dup', methods=['POST'])
# def check_dup():
#     username_receive = request.form['username_give']
#     exists = bool(db.users.find_one({"username": username_receive}))
#     return jsonify({'result': 'success', 'exists': exists})
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        status = payload["id"]
        return render_template('index.html', user_info=user_info, status=status)
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

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
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

@app.route("/search", methods=["POST"])
def post_search():
    keyword_receive = request.form["keyword_give"]
    results = search_keyword(keyword_receive)
    return jsonify({'search_results': results})

@app.route("/all_products", methods=["GET"])
def get_all_products():
    all_products_list = list(db.posting.find({},{'_id':False}))
    return jsonify({'all_products': all_products_list})

@app.route('/posts/<username>')
def post_page(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('write.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/posts', methods=['POST'])
def post():
    post_id = create_post_id()
    print(post_id)

    file = request.files["file_give"]
    file_dir = upload_forder + '/' + file.filename
    file.save(file_dir)
    post_img = '.' + file_dir

    post_product = request.form['post_product_give']
    post_store = request.form['post_store_give']
    post_star = request.form['post_star_give']
    post_content = request.form['post_content_give']

    #### db 저장
    doc = {
        'post_store': post_store,  # dict
        'post_img': post_img,  # string
        'post_content': post_content,  # string
        'post_star': post_star,  # int
        'post_product': post_product,  # string
        'post_id': post_id,  # int
    }
    db.posting.insert_one(doc)
    return jsonify({'msg': '저장완료'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5003, debug=True)