#!/usr/bin/env python

import os

RETHINKDB_HOST=os.getenv('RETHINKDB_HOST',"rethinkdb")
RETHINKDB_DB=os.getenv('RETHINKDB_DB',"siz")
MONGO_HOST=os.getenv('MONGO_HOST',"mongo")
MONGO_DB=os.getenv('MONGO_DB',"siz")
INPUT_S3_BUCKET=os.getenv('INPUT_S3_BUCKET',"static.siz.io")
OUPUT_S3_BUCKET=os.getenv('OUPUT_S3_BUCKET',"fun.siz.io")
STOP_ON_DUPLICATED=(os.getenv('STOP_ON_DUPLICATED',"False")=="True")
DRY_MODE=(os.getenv('DRY_MODE',"False")=="True")
CONVERT_VIDEO=(os.getenv('DRY_MODE',"True")=="True")



from common import *

def old_to_new_box(old_box,new_id,nb):
    return {
       'height' : old_box['height'],
       'width' : old_box['width'],
       'formats' : [
           {'type': 'mp4','href': '//fun.siz.io/stories/'+new_id+'/'+str(nb)+'.mp4'},
           {'type': 'gif','href': '//fun.siz.io/stories/'+new_id+'/'+str(nb)+'.gif'}
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


def old_to_new_result(story):
    from bson import ObjectId
    new_id = old_story_to_new_id(story)
    return {
       'boxes' : old_to_new_boxes(story['boxes'],new_id),
       'creationDate' : int(story['date']),
       '_id' : ObjectId(new_id),
       'slug' : story['id'],
       'source' : old_story_to_source(story),
       'picture' : { 'href': story['pictureUrl'] },
       'title' : story['title'],
       'tags' : old_story_to_tags(story)
    }

old_stories = retrieve_old_stories(RETHINKDB_HOST,RETHINKDB_DB)
new_stories = map(old_to_new_result,old_stories)

import tempfile
tmp_dir = tempfile.mkdtemp()
print 'Tmp working dir : %s' % tmp_dir


ssl_patch_for_boto()
s3_conn = boto.connect_s3()
input_bucket = s3_conn.get_bucket(INPUT_S3_BUCKET)
output_bucket = s3_conn.get_bucket(OUPUT_S3_BUCKET)
collection = get_collection(MONGO_HOST,MONGO_DB)

for i in range(len(new_stories)):
  story = new_stories[i]
  old_story = old_stories[i]
  print '=== %s ===' % story['slug']
  try:
     mongo_story = collection.find_one(story['_id'])
     if mongo_story != None:
        print "already in database"
        if STOP_ON_DUPLICATED:
           break
        else:
           continue
     print "convert mp4 to gif"
     if DRY_MODE:
        continue
     if CONVERT_VIDEO:
         videos_to_convert = old_stories_to_videos([old_story],tmp_dir)
         for video in videos_to_convert:
            convert_and_upload_video(video,input_bucket,output_bucket)

     print 'Insert in mongod %s / %s :' % (story['slug'],story['_id']),
  
     collection.insert(story)
     print 'ok'
  except errors.DuplicateKeyError:
     print 'duplicated in mongo'
     if STOP_ON_DUPLICATED:
        break
  except KeyboardInterrupt:
     break
  except:
     print 'error'

import shutil
shutil.rmtree(tmp_dir)
