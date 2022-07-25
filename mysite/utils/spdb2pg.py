# APP spatialitedb数据入库

import django
import sys
import os
import re

# debug = False
# debug = True
# if debug:
#     sys.path.extend(['/home/song/django/hub04_repo'])
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE','hub.settings')
#     django.setup()

import json
import time
import pytz
import uuid
import sqlite3
# from osgeo import osr
from datetime import datetime

import logging
logger = logging.getLogger()

# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.models import User
# from django.utils.timezone import localtime
# from geodb.models import Veccat, Vecdata, Imagedata

# from hub import settings


class GpapConnection(object):
    def __init__(self, db_name):
        self.db_name = db_name

    def execute(self, statement):
        self._execute_stmt(statement,  False)

    def query(self, query):
        return self._execute_stmt(query, True)

    def _execute_stmt(self, statement, fetch, enable_spatialite=True):
        with sqlite3.connect(self.db_name) as conn:
            if enable_spatialite:
                conn.enable_load_extension(True)
                conn.load_extension("/usr/local/lib/mod_spatialite");

            cursor = conn.cursor()
            cursor.execute(statement)
            if fetch:
                return cursor.fetchall()

    def get_notes(self, clause=None):
        sql = "select _id, lon, lat, ts, form, profile from notes "
        if clause:
            sql += clause
        return self.query(sql)

    def get_images(self, note_id=None):
        sql = """
select im.note_id, im.imagedata_id, im.text, imdata.data, imdata.thumbnail, im.lon, im.lat, im.altim, im.azim, im.ts from 
images im join imagedata imdata on im.imagedata_id=imdata._id join notes n on n._id=im.note_id 
"""
        if note_id:
            sql += f'where im.note_id={note_id}'
        return self.query(sql)


class SpdbConnection(GpapConnection):
    def __init__(self, db_name):
        super().__init__(db_name)
    
    def _execute_stmt(self, statement, fetch, enable_spatialite=True):
        with sqlite3.connect(self.db_name) as conn:
            if enable_spatialite:
                conn.enable_load_extension(True)
                conn.load_extension("/usr/local/lib/mod_spatialite");

        cursor = conn.cursor()
        cursor.execute(statement)
        if fetch:
            return cursor.fetchall()

    def get_table_field(self, tb_name):
        res = self.query("PRAGMA table_info ({tb_name})".format(tb_name=tb_name))
        return res

    def get_spatial_data(self, table_name, cols=[], clause=None):
        print('get {} data from spatialitedb.'.format(table_name))
        cols_str = ''
        if not cols:
            fd_info = self.get_table_field(table_name)
            for i, fd in enumerate(fd_info):
                if fd[1]=='Geometry':
                    cols_str += f'ST_AsText({fd[1]}),'
                else:
                    cols_str += f'{fd[1]},'
        else:
            for i, fd in enumerate(cols):
                if fd=='Geometry':
                    cols_str += f'ST_AsText({fd}),'
                else:
                    cols_str += f'{fd},'
        sql = 'select {} from {}'.format(cols_str[:-1], table_name)
        if clause:
            sql += clause
        return self.query(sql)


def main():
    # conn.load_extension("/usr/lib/mod_spatialite");
    # gpap_name = os.path.join(os.path.dirname(__file__), "geomapper.gpap")
    user_id = 9 # bijie
    group_id = 4
    spdb_name = r'mysite/utils/spatialitedbs_yingwunongye_2022.sqlite'
    conn = SpdbConnection(spdb_name)
    # res = conn.query("PRAGMA table_info (polygon)")
    # res = conn.get_table_field('points')
    # res = conn.get_spatial_data('lines')
    # print(res)

    res = conn.get_spatial_data(table_name='polygon', cols=['field1','Geometry'])
    print(res)

if __name__ == '__main__':
    main()