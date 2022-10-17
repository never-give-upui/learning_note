# -*- coding: utf-8 -*-
'''
Copyright (c) 2016-2022, XYAsset. All rights reserved.

Author: WangYuLong

Create Date: 2022-09-26 13:45:02

Last Time: 2022-10-14 17:41:07

Last Author: YuanLongdi

Description: 
'''
import json
import logging
import requests
config = {}
with open("config/config.json", 'r') as f:
    config = json.load(f)


def check_config():
    try:
        isok = True
        url = config['custom']['公共参数URL']
        config['url'] = url
        res = requests.get(url)
        res_data = res.json()

        decrypt_url = res_data['custom']['公共配置']['解密URL']
        config['decrypt_url'] = decrypt_url
        data = res_data['custom']['公共配置']['REDIS']

        if 'MASTER名称' not in data:
            isok = False
            logging.warning('redis_ttl loss of \'MASTER名称\' 在公共配置config')
        else:
            config['MASTER名称'] = data.get('MASTER名称')
    except Exception as e:
        logging.warning('Could not get config from url :{}'.format(e))
        isok = False
    return isok
