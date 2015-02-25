#!/usr/bin/env python

import os

GIF_COLORS=256
GIF_FPS=6
RETHINKDB_HOST="rethinkdb"
RETHINKDB_DB="siz"
INPUT_S3_BUCKET="static.siz.io"
OUPUT_S3_BUCKET="fun.siz.io"

from common import *

from moviepy.editor import VideoFileClip
def convert_mp4_to_gif(mp4_in,gif_out):
    clip = (VideoFileClip(mp4_in))
    clip.write_gif(gif_out, colors=GIF_COLORS, fps=GIF_FPS)

from urlparse import urlparse
def old_stories_to_videos(stories):
    videos = []
    for story in stories:
        for i in range(len(story['boxes'])):
            box = story['boxes'][i]
            videos.append(
                {
                    'local_prefix_filename' : old_story_to_new_id(story)+'_'+str(i),
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

def convert_and_upload_video(video):
    mp4_file_path = "%s/%s.mp4" % (tmp_dir, video['local_prefix_filename'])
    if retrieve_file_from_s3(input_bucket,video['mp4_key'],mp4_file_path):
        gif_file_path = "%s/%s.gif" % (tmp_dir, video['local_prefix_filename'])
        convert_mp4_to_gif(mp4_file_path,gif_file_path)
        mp4_s3_key = "%s.mp4" % video['output_prefix_key']
        upload_file_to_s3(output_bucket,mp4_s3_key,mp4_file_path)
        gif_s3_key = "%s.gif" % video['output_prefix_key']
        upload_file_to_s3(output_bucket,gif_s3_key,gif_file_path)
        os.remove(mp4_file_path)
        os.remove(gif_file_path)


old_stories = retrieve_old_stories(RETHINKDB_HOST,RETHINKDB_DB)
videos_to_convert = old_stories_to_videos(old_stories)

import tempfile
tmp_dir = tempfile.mkdtemp()
print 'Tmp working dir : %s' % tmp_dir

ssl_patch_for_boto()
s3_conn = boto.connect_s3()
input_bucket = s3_conn.get_bucket(INPUT_S3_BUCKET)
output_bucket = s3_conn.get_bucket(OUPUT_S3_BUCKET)

map(convert_and_upload_video,videos_to_convert)  

import shutil
shutil.rmtree(tmp_dir)
