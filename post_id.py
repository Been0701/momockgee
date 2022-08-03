from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:sparta@cluster0.mndqybx.mongodb.net/Cluster0?retryWrites=true&w=majority")
# client = MongoClient("mongodb+srv://store:food2022@cluster0.himuf.mongodb.net/?retryWrites=true&w=majority")
db = client.momockgee

max_postid_ls = list(db.max_postid.find({},{'_id':False}))
print(max_postid_ls)
if not max_postid_ls:
    cur_max_postid = 0
    db.max_postid.insert_one({'cur_max_postid': 0})
else:
    cur_max_postid = max_postid_ls[0]['cur_max_postid']

def create_post_id():
    global cur_max_postid
    db.max_postid.update_one({'cur_max_postid': cur_max_postid}, {'$set':{'cur_max_postid': cur_max_postid + 1}})
    cur_max_postid += 1
    return cur_max_postid