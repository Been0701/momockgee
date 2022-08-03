from pymongo import MongoClient

client = MongoClient('mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority')
db = client.momockgee

def search_keyword(keyword):
    results = []
    word = keyword.split(" ")
    all_contents = list(db.posting.find({}, {'_id': False}))
    for i in all_contents:
        for j in word:
            if j in i['post_product']:
                results.append(i['post_id'])

    result_id = list(set(results))
    search_contents = list(db.posting.find({'post_id': {'$in': result_id}}, {'_id': False}))
    return search_contents