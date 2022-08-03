from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from search import search_keyword
from store import store_list
import os.path
from post_id import create_post_id

app = Flask(__name__)
client = MongoClient('mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority')
# client = MongoClient("mongodb+srv://test:sparta@cluster0.mndqybx.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.momockgee

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"
SECRET_KEY = 'SPARTA'

upload_forder = './upload'
if not os.path.exists(upload_forder):
    os.makedirs(upload_forder)

# @app.route('/')
# def home():
#    return render_template("index.html")

@app.route('/')
def home():
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    return render_template('index.html')
    # except jwt.ExpiredSignatureError:
    #     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # except jwt.exceptions.DecodeError:
    #     return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

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
    keyword_receive = request.form["keyword_give"]
    results = search_keyword(keyword_receive)
    print(results)
    results_list = store_list(results)
    return jsonify({'search_results': results_list})

@app.route("/all_products", methods=["GET"])
def get_all_products():
    all_products_list = list(db.posting.find({},{'_id':False}))
    products_list = store_list(all_products_list)
    return jsonify({'all_products': products_list})

@app.route('/posts')
def post_page():
   return render_template('write.html')

@app.route('/posts', methods=['POST'])
def post():
    ##### file
    # f = request.files.get('file')
    # file_dir = upload_forder + '/' + f.filename
    # f.save(file_dir)
    # post_img = '.' + file_dir
    # print(post_img)

    ##### create post id
    # post_list = list(db.Posting.find({},{'_id':False}))
    # post_id_list = []
    # for post_dic in post_list:
    #     post_id_list.append(post_dic['post_id'])
    #
    # # print(post_id_list)
    # post_id = random.randint(1, 1e7)
    # while post_id in post_id_list:
    #     # print('in while')
    #     post_id = random.randint(1, 1e7)

    post_id = create_post_id()
    print(post_id)

    ##### 그 외 front에서 받아 올 것
    # post_store = {'CU': 1, 'GS': 0, 'seven': 0, 'ministop': 0, 'emart25': 0}
    # post_content = '너무 맛있고 너무 맛있어요'
    # post_star = 3
    # post_product = '계란과자'
    post_product = request.form["post_product_give"]
    post_store = request.form["post_store_give"]
    post_star = request.form["post_star_give"]
    post_content = request.form["post_content_give"]
    print(post_product, post_store, post_star, post_content)

    ## post_product 문자 모든 공백 제거
    # post_product = post_product.replace(" ", "")

    ##### db 저장
    # doc = {
    #     'post_store': post_store,  # dict
    #     'post_img': post_img,  # string
    #     'post_content': post_content,  # string
    #     'post_star': post_star,  # int
    #     'post_product': post_product,  # string
    #     'post_id': post_id,  # int
    # }
    # db.posting.insert_one(doc)
    return jsonify({'msg': '저장완료'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5005, debug=True)