# _*_ coding: utf-8 _*_
# @Time     :   2020/7/10 19:15
# @Author       vanwhebin

# 处理ups的单据识别
import fitz
import re

from .clip import Clip


class UpsClip(Clip):
	file_type = "ups"
	image_path = 'clips'
	ins = {
		"tk": {
			"br": (185, 5),
			"tl": (235, 110)
		},
		"or": {
			"br": (50, 20),
			"tl": (368, 195)
		}
	}
	code_type = {
		"order": "order_num",
		"track": "tracking_num"
	}

	def clip(self, pdf_p):
		clip_list = []
		pdf_doc = fitz.open(pdf_p)  # open document
		for pg in range(pdf_doc.pageCount):  # iterate through the pages
			page = pdf_doc[pg]
			rect = page.rect  # 页面大小
			if rect.br[1] < rect.br[0]:  # 纵座标小于横左边 表明是横版需要调整为竖版
				rotate = int(90)
			else:
				rotate = int(0)

			# 选择截取的位置面积
			tk_br = rect.br - self.ins['tk']['br']  # 物流订单号矩形区域
			tk_tl = rect.tl + self.ins['tk']['tl']
			or_br = rect.br - self.ins['or']['br']  # 订单号矩形区域
			or_tl = rect.tl + self.ins['or']['tl']

			# 对文件进行放大
			zoom_x = 20
			zoom_y = 20
			mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)  # 缩放系数在每个维度  .preRotate(rotate)是执行一个旋转

			order_num_clip_path = self.save_clip(mat, page, self.file_type + '_' + self.code_type['order'], or_tl, or_br)
			tracking_num_clip_path = self.save_clip(mat, page, self.file_type + '_' + self.code_type['track'], tk_tl, tk_br)
			clip_list.append({"path": order_num_clip_path, "type": self.code_type['order']})
			clip_list.append({"path": tracking_num_clip_path, "type": self.code_type['track']})
		return clip_list

	# @staticmethod
	# def format_text(string):
	# 	"""
	# 	进行清洗格式化，去除噪点
	# 	:param string:
	# 	:return:
	# 	"""
	# 	# pattern = re.compile(r"[\d+\w+]")
	# 	# string_list = pattern.findall(string)
	# 	# string = re.sub(r"\.|/|REF2|:|TRACKING # f|#|\s", '', "".join(string_list))
	# 	# string = re.sub(r"\.|/|REF2|:|TRACKING # f|#|\s", '', string)
	# 	# string = re.sub(r"\dof\d", '', string)
	# 	format_string = re.sub(r"\.|/|:|#|\s", '', string)
	# 	return format_string

	def check_valid(self, code_type, string):
		"""
		检查是否合法
		:param code_type:
		:param string:
		:return:
		"""
		# 获得规则比较
		format_str = self.format_text(string)
		count = len(format_str)
		if count != 11 and code_type == self.code_type['order']:
			return False
		if count != 18 and code_type == self.code_type['track']:
			# 再次调用高精度api进行查询
			return False
		return format_str

