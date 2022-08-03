from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from search import search_keyword

app = Flask(__name__)
client = MongoClient('mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority')
db = client.momockgee

@app.route('/')
def home():
   return render_template("index.html")

@app.route("/search", methods=["POST"])
def post_search():
    product_receive = request.form["product_give"]
    results = search_keyword(product_receive)
    return jsonify({'search_results': results})

@app.route("/all_products", methods=["GET"])
def get_all_products():
    all_products_list = list(db.posting.find({},{'_id':False}))
    return jsonify({'all_products' : all_products_list})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)