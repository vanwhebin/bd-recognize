import os
import time
import uuid
import re
import hashlib
import fitz

from .bd_api import BaiduAPI
from djangodir.settings import MEDIA_ROOT, BASE_DIR
from ocr.utils.fedex_clip import FedexClip
from ocr.utils.ups_clip import UpsClip
from ocr.models import Invoice


class ClipPDF:
	pdfs = []
	log = "log"
	pdf_hash = []
	bd_api = None
	file_type = {
		"fedex": "fedex",
		"ups": "ups",
	}

	def __init__(self):
		self.bd_api = BaiduAPI()
		self.pdfs = []
		self.pdf_hash = []

	def pympdf2_fitz(self, pdf_p, file_type, title):
		"""
		对PDF进行操作，需要转换为图片，进行截取需要识别的文件部分
		:param pdf_p:
		:param file_type
		:param title
		:return:
		"""
		clip_list = []
		handler = None
		if file_type == self.file_type['fedex']:
			handler = FedexClip()
			clip_list = handler.clip(pdf_p, title)
		elif file_type == self.file_type['ups']:
			handler = UpsClip()
			clip_list = handler.clip(pdf_p, title)

		return {"handler": handler, "clip_list": clip_list}

	def handle_api_result(self, it, handler):
		"""
		处理api
		:param it: 文件路径
		:param handler: 处理单据的类
		:return:
		"""
		general_res = self.bd_api.run_general(it['path'])
		self.save_log("general_res" + str(general_res))
		if general_res and "words_result" in general_res:
			check_word_result = handler.check_valid(it['type'], "".join([i['words'] for i in general_res['words_result']]))
			# 检查执行结果
			if not check_word_result:
				time.sleep(1)
				word = self.bd_api.run_accurate(it['path'])
				self.save_log("accurate_res" + str(word))
				return [
					handler.format_text(it['type'], "".join([accurate_item['words'] for accurate_item in word['words_result']]))]
			return [check_word_result]
		else:
			# print(self.get_time() + u' 百度API请求出错:' + str(general_res['error_msg']))
			self.save_log(self.get_time() + u' 百度API请求出错:' + str(general_res['error_msg']))
			return ['']

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
		zoom_x = 20  # PDF放大尺寸
		zoom_y = 20  # PDF放大尺寸
		file_type_dir = MEDIA_ROOT
		rect = pymupdf_obj[0].rect
		type_br = rect.br - (0, 160)  # 物流订单号矩形区域
		type_tl = rect.tl + (0, 120)

		if rect.br[1] < rect.br[0]:  # 纵座标小于横左边 表明是横版需要调整为竖版
			rotate = int(90)
			type_br = rect.br - (100, 0)  # 物流订单号矩形区域
			type_tl = rect.tl + (100, 0)
		else:
			rotate = int(0)

		mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
		clip_name = f'clip_{uuid.uuid1().hex}.png'
		clip = fitz.Rect(type_tl, type_br)  # 将页面转换为图像
		pix = pymupdf_obj[0].getPixmap(matrix=mat, alpha=False, clip=clip)

		if not os.path.exists(file_type_dir):
			os.makedirs(file_type_dir)
		ab_img_path = os.path.join(file_type_dir, clip_name)
		pix.writePNG(ab_img_path)
		file_content = self.bd_api.run_general(ab_img_path)
		self.save_log(file_content)
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
				self.save_log(u'未识别出pdf文件类型, 请手动检查')
		# raise RuntimeError("未识别出pdf文件类型，请手动检查")

		else:
			self.save_log(u'百度API请求出错:' + str(file_content['error_msg']))

	# raise RuntimeError('百度API请求出错:' + str(file_content['error_msg']))

	def handle_pdf(self, item):
		data_list = []
		pdf_path = os.path.join(MEDIA_ROOT, item.location)
		pdf_d = fitz.open(pdf_path)
		file_type = self.get_pdf_type(pdf_d)
		self.save_log(file_type)
		self.save_log(u"获得file type时间: " + self.get_time())
		if file_type:
			item.file_type = file_type

			handler_res = self.pympdf2_fitz(pdf_path, item.file_type, item.title)  # 指定想要的区域转换成图片
			if handler_res and "clip_list" in handler_res:
				for it in handler_res['clip_list']:
					result = self.handle_api_result(it, handler_res['handler'])
					self.save_log(f"获得{it}时间: " + self.get_time())
					self.save_log("check final result" + str(result))
					time.sleep(1.2)
					data_list = data_list + result
					os.remove(it['path'])
				if data_list:
					item.order_num = data_list[0]
					item.tracking_num = data_list[1]
					item.save()

	@staticmethod
	def get_time():
		return str(time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time())))

	def save_log(self, content):
		""" 将爬取数据写入日志文件 """
		log_file = time.strftime("%Y%m%d", time.localtime(time.time())) + '.log'
		cur_dir = os.path.join(BASE_DIR, self.log)

		if not os.path.exists(cur_dir):
			os.makedirs(cur_dir)
		with open(os.path.join(cur_dir, log_file), 'a+', encoding="utf-8") as f:
			f.write(str(content) + os.linesep)
		f.close()

	@staticmethod
	def file_hash(item):
		file_path = os.path.join(MEDIA_ROOT, item.location)
		with open(file_path, 'rb') as f:
			md5obj = hashlib.md5()
			md5obj.update(f.read())
			item.hash = md5obj.hexdigest()
			print(item.hash)
			return item.hash

	def run(self, files):
		"""执行入口"""
		# self.check_multi_page(files)
		for p in files:
			self.handle_pdf(p)
		# 获取文件模板类型 识别order_num等信
		self.save_log(u"所有文件执行完毕")
		return self.pdfs
