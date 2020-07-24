# _*_ coding: utf-8 _*_
# @Time     :   2020/7/10 19:28
# @Author       vanwhebin

import os
import time
import random
import re
from PIL import Image

import fitz

from djangodir.settings import MEDIA_ROOT


class Clip:
	image_path = 'clips'

	def save_clip(self, mat, page, clip_name, tl, br):
		"""
		保存截取的PDF文件转换为图片部分
		:param mat:
		:param page:
		:param clip_name:
		:param tl:
		:param br:
		:return:
		"""
		img_path = os.path.join(MEDIA_ROOT, self.image_path)
		clip_img_name = 'clip_' + clip_name + '_' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '_' + str(
				random.randint(1, 99)) + '.png'
		clip = fitz.Rect(tl, br)  # 将页面转换为图像
		pix = page.getPixmap(matrix=mat, alpha=False, clip=clip)
		if not os.path.exists(img_path):
			os.makedirs(img_path)
		ab_img_path = os.path.join(img_path, clip_img_name)
		pix.writePNG(ab_img_path)  # store image as a PNG
		# self.resize(ab_img_path)
		return ab_img_path

	@staticmethod
	def resize(clip_file_path, zoom=2):
		# zoom = 2  # 截图放大尺寸
		im = Image.open(clip_file_path)
		(x, y) = im.size
		print(x, y)
		x_z = x * zoom
		y_z = y * zoom
		out = im.resize((x_z, y_z), Image.ANTIALIAS)
		out.save(clip_file_path, 'png')

	@staticmethod
	def format_text(string):
		"""
		进行清洗格式化，去除噪点
		:param string:
		:return:
		"""
		format_string = re.sub(r"\.|/|:|#|REF2|TRACKING|\s", '', string)
		return format_string
