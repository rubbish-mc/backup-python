# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018 Too-Naive and contributors
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
import re

RE = re.compile(r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2}).tar.gz$')

def backupThread():
	Log.info('Starting backup function')
	while True:
		now_time = datetime.now().strftime('%Y%m%d_%H%M%S')
		os.system("tar czfP {}/{}.tar.gz {}/world".format(Config.backup.webroot, now_time, Config.backup.mc_path))
		try:
			with open('{}/LATEST2'.format(Config.backup.webroot), 'w') as fout, open('{}/LATEST'.format(Config.backup.webroot)) as fin:
				fout.write(fin.read())
		except IOError: pass
		with open('{}/LATEST'.format(Config.backup.webroot), 'w') as fout:
			fout.write(now_time)
		Log.info('{}.tar.gz backuped.', now_time)
		fileChecking(Config.backup.webroot)
		time.sleep(Config.backup.interval)

def mainRequest(LATEST):
	r = requests.get('{}/LATEST'.format(Config.backup.website), timeout=10)
	if LATEST == r.text:
		return LATEST
	_LATEST = LATEST
	LATEST = r.text
	s = requests.get('{}/{}.tar.gz'.format(Config.backup.website, LATEST), stream=True, timetout=10)
	try:
		s.raise_for_status()
	except Exception as e:
		Log.error('Catched Exception:`{}\'', repr(e))
		return _LATEST
	# From: https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
	with open("{}/{}.tar.gz".format(Config.backup.download_path, LATEST), 'wb') as fout:
		for chunk in s.iter_content(chunk_size=1024):
			if not chunk: break
			fout.write(chunk)
	Log.info('{}.tar.gz downloaded.', LATEST)
	fileChecking(Config.backup.download_path)
	return LATEST

def requestThread():
	LATEST = None
	while True:
		try:
			LATEST = mainRequest(LATEST)
		except: Log.write_traceback_error('Error while requesting file')
		finally: time.sleep(Config.backup.interval)

def fileChecking(path):
	current_time = datetime.now().replace(microsecond=0)
	for roots, dirs, files in os.walk(path):
		if roots == path:
			for x in files:
				r = RE.match(x)
				if r and \
					(current_time-datetime(*(int(n) for n in r.groups()))).total_seconds() > Config.backup.interval*3:
						os.remove('{}/{}'.format(path, x))

if __name__ == '__main__':
	if len(argv) == 2 and argv[1] == '--backup':
		backupThread()
	elif len(argv) == 2 and argv[1] == '--download':
		requestThread()
	else:
		pass
