#!/usr/bin/env python

RETHINKDB_HOST="rethinkdb"
RETHINKDB_DB="siz"
MONGO_HOST="mongo"
MONGO_DB="siz"

from common import *

def old_to_new_box(old_box,new_id,nb):
    return {
       'height' : old_box['height'],
       'width' : old_box['width'],
       'formats' : [
           {'type': 'mp4','href': '//fun.siz.io/stories/'+new_id+'/'+str(nb)+'.mp4'},
           {'type': 'gif','href': '//fun.siz.io/stories/'+new_id+'/'+str(nb)+'.gif'},
       ]
    }

def old_to_new_boxes(old_boxes,new_id):
    boxes = []
    for i in range(len(old_boxes)):
        boxes.append(old_to_new_box(old_boxes[i],new_id,i))
    return boxes




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

from datetime import datetime
def mstimestamp_to_date(mstimestamp):
    return datetime.fromtimestamp(mstimestamp/1000).replace(microsecond = (mstimestamp % 1000) * 1000)

def old_to_new_result(story):
    from bson import ObjectId
    new_id = old_story_to_new_id(story)
    return {
       'boxes' : old_to_new_boxes(story['boxes'],new_id),
       'creationDate' : mstimestamp_to_date(story['date']),
       '_id' : ObjectId(new_id),
       'slug' : story['id'],
       'source' : old_story_to_source(story),
       'picture' : { 'href': story['pictureUrl'] },
       'title' : story['title'],
       'tags' : old_story_to_tags(story)
    }

old_stories = retrieve_old_stories(RETHINKDB_HOST,RETHINKDB_DB)
new_stories = map(old_to_new_result,old_stories)

save_new_stories(new_stories,MONGO_HOST,MONGO_DB)
