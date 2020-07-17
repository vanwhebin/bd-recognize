# _*_ coding: utf-8 _*_
# @Time     :   2020/7/10 19:15
# @Author       vanwhebin

# 处理fedex的单据识别
import fitz
import re

from .clip import Clip


class FedexClip(Clip):
	file_type = "fedex"
	image_path = 'clips'
	ins = {
		"tk": {
			"br": (150, 160),
			"tl": (0, 240)
		},
		"or": {
			"br": (200, 290),
			"tl": (0, 128)
		}
	}

	def clip(self, pdf_p):
		clip_list = []
		pdf_doc = fitz.open(pdf_p)  # open document
		for pg in range(pdf_doc.pageCount):  # iterate through the pages
			page = pdf_doc[pg]
			rect = page.rect  # 页面大小
			# print("高", rect.br[1])
			# print("长", rect.tr[0])
			if rect.br[1] < rect.tr[0]:  # 纵座标小于横左边 表明是横版需要调整为竖版
				rotate = int(90)
			else:
				rotate = int(0)

			# 选择截取的位置面积
			tk_br = rect.br - (150, 170)  # 物流订单号矩形区域
			tk_tl = rect.tl + (0, 240)
			or_br = rect.br - (200, 290)  # 订单号矩形区域
			or_tl = rect.tl + (0, 128)

			# 对文件进行放大
			zoom_x = 20
			zoom_y = 20
			mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)  # 缩放系数在每个维度  .preRotate(rotate)是执行一个旋转

			order_num_clip_path = self.save_clip(mat, page, self.file_type + '_order_num', or_tl, or_br)
			tracking_num_clip_path = self.save_clip(mat, page, self.file_type + '_tracking_num', tk_tl, tk_br)
			clip_list.append(order_num_clip_path)
			clip_list.append(tracking_num_clip_path)
		return clip_list

	@staticmethod
	def format_text(string):
		"""
		进行清洗格式化，去除噪点
		:param string:
		:return:
		"""
		string = re.sub(r"PO|TRK|MPS|\.|/|:|#|\s", '', string)
		string = re.sub(r"\dof\d", '', string)
		return string

	def check_valid(self, string):
		"""
		检查是否合法
		:param string:
		:return:
		"""
		# 获得规则比较
		format_str = self.format_text(string)
		count = len(format_str)
		if count != 11 and count != 12:
			# 再次调用高精度api进行查询
			return False
		return format_str
