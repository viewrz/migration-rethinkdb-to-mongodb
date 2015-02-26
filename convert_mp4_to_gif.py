#!/usr/bin/env python

import os

RETHINKDB_HOST="rethinkdb"
RETHINKDB_DB="siz"
INPUT_S3_BUCKET="static.siz.io"
OUPUT_S3_BUCKET="fun.siz.io"

from common import *

old_stories = retrieve_old_stories(RETHINKDB_HOST,RETHINKDB_DB)

import tempfile
tmp_dir = tempfile.mkdtemp()
print 'Tmp working dir : %s' % tmp_dir

videos_to_convert = old_stories_to_videos(old_stories,tmp_dir)

ssl_patch_for_boto()
s3_conn = boto.connect_s3()
input_bucket = s3_conn.get_bucket(INPUT_S3_BUCKET)
output_bucket = s3_conn.get_bucket(OUPUT_S3_BUCKET)

for video in videos_to_convert:
    convert_and_upload_video(video,input_bucket,output_bucket)

import shutil
shutil.rmtree(tmp_dir)
