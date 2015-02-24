#/usr/bin/env python

from moviepy.editor import VideoFileClip

GIF_COLORS=256
GIF_FPS=6
RETHINKDB_HOST="rethinkdb"
RETHINKDB_DB="siz"
MONGO_HOST="mongo"
MONGO_DB="siz"

def convert_mp4_to_gif(mp4_in,gif_out):
    clip = (VideoFileClip(mp4_in))
    clip.write_gif(gif_out, colors=GIF_COLORS, fps=GIF_FPS)

def retrieve_old_stories():
    import rethinkdb as r
    connection = r.connect(RETHINKDB_HOST, 28015)
    db = r.db(RETHINKDB_DB)

    old_stories = db.table('video').has_fields('boxes').order_by(r.desc('date')).eq_join('shortlist',db.table('shortlist')).pluck({ "left": True, "right" : { "category": True }}).zip().run(connection)
    return old_stories

def old_to_new_box(old_box):
    return {
       'height' : old_box['height'],
       'width' : old_box['width'],
       'formats' : [{'type': 'mp4','href': old_box['url']}]
    }

def old_to_new_boxes(old_boxes):
    return map(old_to_new_box,old_boxes)

def old_to_new_id(oldId, date):
    import hashlib
    return str(date)+hashlib.md5(oldId).hexdigest()[:11]

def old_story_to_tags(story):
    tags = [story["shortlist"]]
    if "category" in story:
        tags.append(story["category"])
    return tags

def old_story_to_source(story):
    source = {
          'id' : story['sourceId'],
          'type' : story['source']
       }
    if "duration" in story:
        source['duration'] = int(story['duration']*1000.0)
    return source

def mstimestamp_to_date(mstimestamp):
    from datetime import datetime
    return datetime.fromtimestamp(mstimestamp/1000).replace(microsecond = (mstimestamp % 1000) * 1000)

def old_to_new_result(story):
    from bson import ObjectId
    return {
       'boxes' : old_to_new_boxes(story['boxes']),
       'creationDate' : mstimestamp_to_date(story['date']),
       'id' : ObjectId(old_to_new_id(story['id'],story['date'])),
       'slug' : story['id'],
       'source' : old_story_to_source(story),
       'picture' : { 'href': story['pictureUrl'] },
       'title' : story['title'],
       'tags' : old_story_to_tags(story)
    }


def save_new_stories(stories):
    from pymongo import MongoClient
    client = MongoClient(MONGO_HOST, 27017)
    db = client[MONGO_DB]
    collection = db['stories']
    collection.insert(stories)

old_stories = retrieve_old_stories()
new_stories = map(old_to_new_result,old_stories)

save_new_stories(new_stories)
