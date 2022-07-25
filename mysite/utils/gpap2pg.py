# APP gpap数据入库
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
from osgeo import osr
from datetime import datetime

import logging
logger = logging.getLogger()

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from geodb.models import Veccat, Vecdata, Imagedata

from hub import settings


class GpapConnection(object):
    def __init__(self, db_name):
        self.db_name = db_name

    def execute(self, statement):
        self._execute_stmt(statement,  False)

    def query(self, query):
        return self._execute_stmt(query, True)

    def _execute_stmt(self, statement, fetch):
        with sqlite3.connect(self.db_name) as conn:
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


def write_image_data(gpap_name, mediapath, user_id, group_id, cat_id, note_id, vecdata_id):
    logger.info('保存note图片数据...\ngpap_name:{}, user_id:{}, note_id:{}'.format(
        gpap_name, user_id, note_id))

    gpapconn = GpapConnection(gpap_name)

    icon_dir  = '%s/icon'  % (mediapath)
    img_dir = '%s/image' % (mediapath)
    
    imgdata = gpapconn.get_images(note_id)
    img_ext = 'jpg'

    note_imgs = []
    # 保存图片到用户目录
    for data in imgdata:
        note_id = data[0]
        im_uuid = uuid.uuid4()
        im_name = f'{im_uuid}.{img_ext}'
        im_path = os.path.join(img_dir, im_name)
        icon_path = os.path.join(icon_dir, im_name)
        note_imgs.append(
            {'note_id': note_id, 'im_uuid':im_uuid, 
            'text': data[2], 'ext': os.path.splitext(data[2])[-1],
            'lon': data[5], 'lat': data[6],
            'altim': data[7], 'azim': data[8], 'ts': data[9]}
        )
        with open(im_path, 'wb') as f:
            f.write(data[3])
        with open(icon_path, 'wb') as f:
            f.write(data[4])

    logger.info('note_imgs={}'.format(note_imgs))
    # 记录图片信息到geodb_imagedata表
    for note_img in note_imgs:
        tim = datetime.fromtimestamp(note_img['ts']/1000.0)
        tim_china_tz = tim.astimezone(pytz.timezone('Asia/Shanghai'))
        logger.info('note image tim_china_tz: {}'.format(tim_china_tz))

        dat = Imagedata.objects.create(
            title=note_img['text'],
            abstract='',
            name=note_img['im_uuid'], 
            ext=note_img['ext'], 
            mime='image/'+note_img['ext'][1:],
            lon=note_img['lon'],
            lat=note_img['lat'],
            alt=note_img['altim'], 
            azm=note_img['azim'], 
            # tim = tim,
            dat_id=vecdata_id, 
            cat_id=cat_id, 
            user_id=user_id, 
            group_id=group_id,
            # _created=tim,
            # _modified=tim
        )
        dat.save()
        dat.tim = tim_china_tz
        dat._created = tim_china_tz
        dat._modified = tim_china_tz
        dat.save()


def write_notes_to_db(gpap_name, imgs_dir, user_id, group_id, cat_id):
    logger.info('gpap_name:{}, user_id:{}'.format(
        gpap_name, user_id))
    gpapconn = GpapConnection(gpap_name)

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)  #wgs84
    target = osr.SpatialReference()
    target.ImportFromEPSG(3857)  #Google
    coordTrans = osr.CoordinateTransformation(source, target)
    
    notes = gpapconn.get_notes(clause='order by ts asc')
    for note in notes:
        ts = note[3] # gpap note timestamp
        note_tim = datetime.fromtimestamp(ts/1000.0)
        logger.info('note id:{}, note_tim:{}, note_profile: {}'.format(
            note[0], note_tim, note[5]))

        section = json.loads(note[4])
        
        # 从profile_name解析cat_id
        if cat_id is None:
            if len(note[5])>0:
                # <YYYY>年<name>-<username>-<cat_id> 
                m = re.match(r"^20\d\d.+-.+-([0-9]+)$", note[5])
                cat_id = m.group(1) if m else None
                if cat_id is None:
                    logger.info('未指定目标图层!')
                    continue
            else:
                logger.info('未指定目标图层!')
                continue
        else:
            cat_id = int(cat_id)
        # 表单数据插入到指定矢量图层
        try:
            cat = Veccat.objects.get(id=cat_id)
        except ObjectDoesNotExist:
            logger.info('未查询到图层(cat_id:{})!'.format(cat_id))
            continue

        # 根据note ts字段检查note数据是否需要入库(与库中vecdata数据比较时间)
        note_tim_china_tz = note_tim.astimezone(pytz.timezone('Asia/Shanghai'))
        vecdata = Vecdata.objects.filter(user_id=user_id,cat_id=cat_id).order_by('-_created')
        # vecdata_tz = vecdata[0]._created.tzinfo
        if vecdata.count() > 0:
            # utc时区转换本地时区比较
            latest_created = localtime(vecdata[0]._created)
            if note_tim_china_tz <= latest_created:
                logger.info('note数据为旧数据，不需入库。note id: {}, note_tim_china_tz:{}, latest_created:{}'.format(
                    note[0], note_tim_china_tz, latest_created))
                continue
            logger.info('note数据入库中... note id: {}, note_tim_china_tz:{}, latest_created:{}'.format(
                note[0], note_tim_china_tz, latest_created))

        # 关联矢量图层字段和表单字段
        fd_alias_dict = {}
        for k,v in cat.field.items():
            fd_alias_dict.update({v['alias']: k})
        
        logger.info('fd_alias_dict = {}'.format(fd_alias_dict))

        forms = section['forms']
        prop = {}
        for form in forms:
            formitems = form['formitems']
            for item in formitems:
                item_label = item['label'] if 'label' in item else item['key']
                if item_label not in fd_alias_dict:
                    continue
                fd = fd_alias_dict[item_label]
                logger.info('fd={}, value={}'.format(fd, item['value']))

                if item['type']!='dynamicgroup':
                    prop.update({fd: item['value']})
                else:
                    children_data = []
                    children_form = item['children']
                    children_form_keys = [ck['key'] for ck in children_form]
                    logger.info('- children_form_keys =  {}'.format(children_form_keys))
                    cform_values = item['value'].split('#')
                    for cform_val in cform_values:
                        vals = cform_val.split('&')
                        child_data = {}
                        for idx, val in enumerate(vals):
                            child_data.update({children_form_keys[idx]: val})
                        children_data.append(child_data)
                    logger.info(' children_data = {} '.format(children_data))
                    prop.update({fd: children_data})

        lon = note[1]
        lat = note[2]
        x,y,z = coordTrans.TransformPoint(lat,lon)
        geom = 'Point(%f %f)' % (x,y)

        dat = Vecdata.objects.create(
            geom=geom,
            prop=prop,
            cat_id=cat_id,
            user_id=user_id,
            group_id=group_id
        )
        dat.save()
        # 更新Vecdata _created为APP note数据的创建时间
        dat._created = note_tim_china_tz
        dat._modified = note_tim_china_tz
        dat.save()
        logger.info('note入库成功, note id={}, Vecdata id={}, dat._created={}'.format(note[0], dat.id,dat._created))

        write_image_data(gpap_name, imgs_dir, user_id, group_id, cat.id, note[0], dat.id)

def delete_data(user_id, cat_id, mediapath):
    icon_dir  = '%s/icon'  % (mediapath)
    img_dir = '%s/image' % (mediapath)

    imgdata = Imagedata.objects.filter(user_id=user_id,cat_id=cat_id)
    vecdata = Vecdata.objects.filter(user_id=user_id,cat_id=cat_id)

    def delete_file(fpath):
        if os.path.exists(fpath):
            os.remove(fpath)
            print('文件: {} 已删除'.format(fpath))
        else:
            print('文件: {} 不存在'.format(fpath))
    
    for d in imgdata:
        im_name = d.name + d.ext
        im_path = os.path.join(img_dir, im_name)
        icon_path = os.path.join(icon_dir, im_name)
        delete_file(im_path)
        delete_file(icon_path)
        d.delete()

    for d in vecdata:
        print(d.id)
        d.delete()


def test():    
    users = User.objects.all()
    users.count()
    #
    # users = User.objects.filter(username__startswith='bijie')
    # print(users.count())
    users = User.objects.filter(username__startswith='bijie1')
    print(users.count())
    # users = User.objects.filter(username__startswith='bijie5')
    # print(users.count())
    #county, xian
    ulist = [u.username for u in users if len(u.username)==11]
    print(len(ulist))
    #station, yanzhan
    ulist = [u.username for u in users if len(u.username)==13]
    print(len(ulist))
    #sites, shougou dian/xian
    ulist = [u.username for u in users if len(u.username)>=14]
    print(len(ulist))
    # for u in users:
    #     print(u.username)
    #     print(u)

def main():
    # gpap_name = os.path.join(os.path.dirname(__file__), "geomapper.gpap")
    # gpap_name = os.path.join(os.path.dirname(__file__), "project_yizai2021_v2.gpap")
    gpap_name = r"/home/song/django/geopapa_repo/project_yizai2021_v2.gpap"
    user_id = 9 # bijie
    group_id = 4

    # user = User.objects.get(username='bijie13595751286')
    # user = User.objects.get(username='bijie')
    # workspace = user.userprofile._workspace
    # mediapath = '%s/workspaces/users/%s/public/media' % (settings.BASE_DIR,workspace)
    # if not os.path.exists(mediapath):
    #     os.makedirs(mediapath)
    # /home/song/django/hub04_repo/workspaces/users/bijie13595751286/public/media

    veccat_alias_filter = [
        '毕节APP打点',
        # '毕节APP灾害上报'
    ]
    # write_notes_to_db(gpap_name, mediapath, user_id, group_id, veccat_alias_filter=veccat_alias_filter)
    # write_notes_to_db(gpap_name, mediapath, user_id, group_id, veccat_alias_filter=None)

    # cat_id = 305 # 图层bijie_app_yizai
    # cat_id = 328 # bijie_app_disaster_report
    # cat_id = 331
    # delete_data(user.id, cat_id, mediapath)

    print('ok')


if __name__ == '__main__':
    main()
    