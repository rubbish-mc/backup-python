# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2017-2018 Too-Naive and contributors
#
# This module is part of ingress-farm-bot and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import time
from datetime import datetime
from libpy.Config import Config
from libpy import Log
import os
import requests
from sys import argv

def backupThread():
    Log.info('Starting backup function')
    while True:
        now_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.system("tar czf {}/{}.tar.gz {}/world/".format(Config.backup.webroot, now_time, Config.backup.mc_path))
        with open('{}/LATEST'.format(Config.backup.webroot)) as fout:
            fout.write(now_time)
        Log.info('{}.tar.gz backuped.', now_time)
        time.sleep(Config.backup.interval)

def requestThread():
    LASTEST = None
    while True:
        r = requests.get('{}/LATEST'.format(Config.backup.website))
        if LASTEST == r.context:
            time.sleep(Config.backup.interval)
            continue
        s = requests.get('{}/{}'.format(Config.backup.website, LASTEST), stream=True)
        # From: https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        with open("{}/{}.tar.gz".format(Config.backup.download_path, r.context), 'wb') as fout:
            for chunk in s.iter_content(chunk_size=1024):
                if chunk:
                    fout.write(chunk)
        Log.info('{}.tar.gz downloaded.', LASTEST)
        time.sleep(Config.backup.interval)

if __name__ == '__main__':
    if len(argv) == 2 and argv[1] == '--backup':
        backupThread()
    elif len(argv) == 2 and argv[1] == '--download':
        requestThread()
    else:
        pass
