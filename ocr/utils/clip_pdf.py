import os
import time
import uuid
import re

import fitz

from .bd_api import BaiduAPI
from djangodir.settings import MEDIA_ROOT
from ocr.utils.fedex_clip import FedexClip
from ocr.utils.ups_clip import UpsClip
from ocr.models import Invoice


class ClipPDF:
	pdfs = []
	bd_api = None
	file_type = {
		"fedex": "fedex",
		"ups": "ups",
	}

	def __init__(self):
		self.bd_api = BaiduAPI()
		self.pdfs = []

	def pympdf2_fitz(self, pdf_p, file_type):
		"""
		对PDF进行操作，需要转换为图片，进行截取需要识别的文件部分
		:param pdf_p:
		:param file_type:
		:return:
		"""
		clip_list = []
		handler = None
		if file_type == self.file_type['fedex']:
			handler = FedexClip()
			clip_list = handler.clip(pdf_p)
		elif file_type == self.file_type['ups']:
			handler = UpsClip()
			clip_list = handler.clip(pdf_p)

		return {"handler": handler, "clip_list": clip_list}

	def handle_api_result(self, it, handler):
		"""
		处理api
		:param it: 文件路径
		:param handler: 处理单据的类
		:return:
		"""
		general_res = self.bd_api.run_general(it)
		# print(general_res)
		if general_res and "words_result" in general_res:
			for i in general_res['words_result']:
				# 检查执行结果
				check_word_result = handler.check_valid(i['words'])
				if not check_word_result:
					time.sleep(1)
					word = self.bd_api.run_accurate(it)
					# print(word)
					return [handler.format_text(accurate_item['words']) for accurate_item in word['words_result']]
				return [check_word_result]
		else:
			print(u'百度API请求出错:' + str(general_res['error_msg']))
			return ['']
			# raise RuntimeError('百度API请求出错:' + str(general_res['error_msg']))

	def check_multi_page(self, files):
		"""
		判断是否是多页pdf，进行分拆
		:param files:
		:return:
		"""
		for f in files:
			pdf_p = os.path.join(MEDIA_ROOT, f.location)
			dir_name = os.path.split(f.location)[0]

			pdf_doc = fitz.open(pdf_p)
			if pdf_doc.pageCount > 1:
				for pg in range(pdf_doc.pageCount):
					multi_page_pdf = fitz.open(pdf_p)
					cur_pdf_name = f"{f.title[:-4]}-{pg+1}.pdf"
					# time.sleep(1)  # 防止循环超过每秒两次的qps限制
					cur_pdf_path = os.path.join(os.path.join(MEDIA_ROOT, dir_name), cur_pdf_name)
					multi_page_pdf.select((pg,))
					multi_page_pdf.save(cur_pdf_path)
					cur_pdf = Invoice.objects.create(
						location=os.path.join(dir_name, cur_pdf_name),
						title=cur_pdf_name
					)
					self.pdfs.append(cur_pdf)
					# multi_page_pdf.close()
			else:
				self.pdfs.append(f)

		return self.pdfs

	def get_pdf_type(self, pymupdf_obj):
		""" 判断PDF票据的类型 """
		zoom_x = 20
		zoom_y = 20
		file_type_dir = MEDIA_ROOT
		rect = pymupdf_obj[0].rect

		if rect.br[1] < rect.br[0]:  # 纵座标小于横左边 表明是横版需要调整为竖版
			rotate = int(90)
		else:
			rotate = int(0)

		mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
		clip_name = f'clip_{uuid.uuid1().hex}.png'
		pix = pymupdf_obj[0].getPixmap(matrix=mat, alpha=False)

		if not os.path.exists(file_type_dir):
			os.makedirs(file_type_dir)
		ab_img_path = os.path.join(file_type_dir, clip_name)
		pix.writePNG(ab_img_path)
		file_content = self.bd_api.run_general(ab_img_path)
		print(file_content)
		os.remove(ab_img_path)
		# print(file_content)

		if file_content and 'words_result' in file_content:
			content_list = [i['words'] for i in file_content['words_result']]
			content = "".join(content_list)

			if re.search("TRK|MPS|FedEx|ORDER", content):
				return self.file_type['fedex']
			elif re.search("REF2|UPS|TRACKING", content):
				return self.file_type['ups']
			else:
				print(u'未识别出pdf文件类型, 请手动检查')
			# raise RuntimeError("未识别出pdf文件类型，请手动检查")

		else:
			print(u'百度API请求出错:' + str(file_content['error_msg']))
		# raise RuntimeError('百度API请求出错:' + str(file_content['error_msg']))

	def handle_pdf(self, item):
		data_list = []
		# print(item.location)
		pdf_path = os.path.join(MEDIA_ROOT, item.location)
		pdf_d = fitz.open(pdf_path)
		file_type = self.get_pdf_type(pdf_d)
		print(file_type)
		if file_type:
			item.file_type = file_type

			handler_res = self.pympdf2_fitz(pdf_path, item.file_type)  # 指定想要的区域转换成图片
			if handler_res and "clip_list" in handler_res:
				for it in handler_res['clip_list']:
					result = self.handle_api_result(it, handler_res['handler'])
					time.sleep(0.5)
					data_list = data_list + result
					os.remove(it)
				if data_list:
					item.order_num = data_list[0]
					item.tracking_num = data_list[1]
					item.save()

	def run(self, files):
		"""执行入口"""
		# self.check_multi_page(files)
		for p in files:
			self.handle_pdf(p)
		# 获取文件模板类型 识别order_num等信
		print(u"所有文件执行完毕")
		return self.pdfs

