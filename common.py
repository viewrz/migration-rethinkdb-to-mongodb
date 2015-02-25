def retrieve_old_stories(host, db):
    import rethinkdb as r
    connection = r.connect(host, 28015)
    db = r.db(db)

    old_stories = db.table('video').has_fields('boxes').order_by(r.desc('date')).eq_join('shortlist',db.table('shortlist')).pluck({ "left": True, "right" : { "category": True }}).zip().run(connection)
    return old_stories

def save_new_stories(stories,host,db):
    from pymongo import MongoClient
    client = MongoClient(host, 27017)
    db = client[db]
    collection = db['stories']
    collection.insert(stories)

import hashlib
def old_story_to_new_id(story):
    return str(story['date'])+hashlib.md5(story['id']).hexdigest()[:11]