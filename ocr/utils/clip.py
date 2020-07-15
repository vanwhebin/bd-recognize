# _*_ coding: utf-8 _*_
# @Time     :   2020/7/10 19:28
# @Author       vanwhebin

import os
import time
import random

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
		clip_name = clip_name + '_' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '_' + str(
				random.randint(1, 99))
		clip = fitz.Rect(tl, br)  # 将页面转换为图像
		pix = page.getPixmap(matrix=mat, alpha=False, clip=clip)
		if not os.path.exists(img_path):
			os.makedirs(img_path)
		ab_img_path = os.path.join(img_path, f'clip_{clip_name}.png')
		pix.writePNG(ab_img_path)  # store image as a PNG
		return ab_img_path

	def save_db(self):
		""" 保存到数据库 """
		pass
