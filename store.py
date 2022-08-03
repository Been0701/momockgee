def store_list(list):
    store_update = list
    for i in list:
        store = []
        temp = i['post_store']
        for (key, value) in temp.items():
            if value == 1:
                store.append(key)
        i['post_store'] = store
    return store_update
