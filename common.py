GIF_COLORS=256
GIF_FPS=6

import os

def retrieve_old_stories(host, db):
    import rethinkdb as r
    connection = r.connect(host, 28015)
    db = r.db(db)

    old_stories = db.table('video').has_fields('boxes').order_by(r.desc('date')).eq_join('shortlist',db.table('shortlist')).pluck({ "left": True, "right" : { "category": True }}).zip().run(connection)
    return old_stories

from pymongo import MongoClient,errors
def save_new_stories(stories,host,db):
    client = MongoClient(host, 27017)
    db = client[db]
    collection = db['stories']
    for storie in stories:
      print 'Insert %s :' % storie['slug'],
      try:
          collection.insert(storie)
          print 'ok'
      except errors.DuplicateKeyError:
          print 'duplicated'

import hashlib
def old_story_to_new_id(story):
    return str(story['date'])+hashlib.md5(story['id']).hexdigest()[:11]

from moviepy.editor import VideoFileClip
def convert_mp4_to_gif(mp4_in,gif_out):
    clip = (VideoFileClip(mp4_in))
    clip.write_gif(gif_out, colors=GIF_COLORS, fps=GIF_FPS)

from urlparse import urlparse
def old_stories_to_videos(stories,work_dir):
    videos = []
    for story in stories:
        for i in range(len(story['boxes'])):
            box = story['boxes'][i]
            videos.append(
                {
                    'local_prefix_filename' : work_dir+old_story_to_new_id(story)+'_'+str(i),
                    'mp4_key' : urlparse(box['url']).path[1:], 
                    'output_prefix_key' : 'stories/'+old_story_to_new_id(story)+'/'+str(i)
                })
    return videos

def ssl_patch_for_boto():
    import ssl

    _old_match_hostname = ssl.match_hostname

    def _new_match_hostname(cert, hostname):
       if hostname.endswith('.s3.amazonaws.com'):
          pos = hostname.find('.s3.amazonaws.com')
          hostname = hostname[:pos].replace('.', '') + hostname[pos:]
       return _old_match_hostname(cert, hostname)

    ssl.match_hostname = _new_match_hostname

import boto
def retrieve_file_from_s3(bucket,key,local_file):
    s3_key = bucket.get_key(key)
    print 'Download %s/%s to %s:' % (bucket.name, key,local_file), 
    if s3_key != None:
        s3_key.get_contents_to_filename(local_file)
        print 'ok'
        return True
    else:
        print 'failed'
        return False

def upload_file_to_s3(bucket,key,local_file):
    s3_key = boto.s3.key.Key(bucket)
    s3_key.key = key
    print 'Upload %s to  %s/%s :' % (local_file, bucket.name, key), 
    s3_key.set_contents_from_filename(local_file)
    print 'ok'

def convert_and_upload_video(video,input_bucket,output_bucket):
    mp4_file_path = "%s.mp4" % video['local_prefix_filename']
    gif_file_path = "%s.gif" % video['local_prefix_filename']
    mp4_s3_key = "%s.mp4" % video['output_prefix_key']
    gif_s3_key = "%s.gif" % video['output_prefix_key']

    if retrieve_file_from_s3(input_bucket,video['mp4_key'],mp4_file_path):
        convert_mp4_to_gif(mp4_file_path,gif_file_path)
        upload_file_to_s3(output_bucket,mp4_s3_key,mp4_file_path)
        upload_file_to_s3(output_bucket,gif_s3_key,gif_file_path)
        os.remove(mp4_file_path)
        os.remove(gif_file_path)