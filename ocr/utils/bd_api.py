# _*_ coding: utf-8 _*_
# @Time     :   2020/7/8 18:11
# @Author       vanwhebin

from libs.aip import AipOcr
from djangodir.settings import BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY


class BaiduAPI:
	# BAIDU_APP_ID = '19547688'
	# BAIDU_API_KEY = '36TjcLXSGlP2In46SBGzpsO3'
	# BAIDU_SECRET_KEY = 'OmY6bieqW4oQLpoGV2EWhg7m3tSCGY34'
	bd_client = {}
	options = {
		"language_type": "ENG",
		"detect_direction": "false"
	}

	def __init__(self):
		self.bd_client = AipOcr(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

	@staticmethod
	def get_file_content(file_path):
		with open(file_path, 'rb') as fp:
			return fp.read()

	def run_general(self, img_path):
		img = self.get_file_content(img_path)
		return self.bd_client.basicGeneral(img, self.options)

	def run_accurate(self, img_path):
		img = self.get_file_content(img_path)
		return self.bd_client.basicAccurate(img, self.options)
