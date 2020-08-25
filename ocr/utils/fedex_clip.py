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
			# "br": (170, 170), 20200805为兼容新物流pdf
			"br": (160, 145),
			"tl": (30, 248)
		},
		"or": {
			"br": (228, 290),
			"tl": (22, 130)
		}
	}
	code_type = {
		"order": "order_num",
		"track": "tracking_num"
	}

	def clip(self, pdf_p, title):
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
			tk_br = rect.br - self.ins['tk']['br']  # 物流订单号矩形区域
			tk_tl = rect.tl + self.ins['tk']['tl']
			or_br = rect.br - self.ins['or']['br']  # 订单号矩形区域
			or_tl = rect.tl + self.ins['or']['tl']

			# 对文件进行放大
			zoom_x = 20
			zoom_y = 20
			mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)  # 缩放系数在每个维度  .preRotate(rotate)是执行一个旋转
			title_prefix = self.file_type + '_' + title + '_'
			order_num_clip_path = self.save_clip(mat, page, title_prefix + self.code_type['order'], or_tl, or_br)
			tracking_num_clip_path = self.save_clip(mat, page, title_prefix + self.code_type['track'], tk_tl, tk_br)
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
	# 	# string = re.sub(r"PO|TRK|MPS|\.|/|:|#|\s", '', "".join(string_list))
	# 	# string = re.sub(r"PO|TRK|MPS|\.|/|:|#|\s", '', string)
	# 	# string = re.sub(r"\dof\d", '', string)
	# 	format_string = re.sub(r"\.|/|:|#|\s", '', string)
	# 	return format_string

	def check_valid(self, code_type, string):
		"""
		检查是否合法
		:param code_type: code類型
		:param string:
		:return:
		"""
		# 获得规则比较
		format_str = self.format_text(code_type, string)
		count = len(format_str)
		if code_type == self.code_type['order']:
			if count != 11:
				return False
			if not re.match(r"[A-Z]{2}\d{9}", format_str):
				return False
		if code_type == self.code_type['track']:
			# 再次调用高精度api进行查询
			if count != 12:
				return False
			if not re.match(r"\d{12}", format_str):
				return False
		return format_str

	def format_text(self, code_type, string):
		# 进行清洗格式化，去除噪点
		for_str = re.sub(r"\s", '', string)
		for_str = re.sub(r"\dof\d", '', for_str)
		pattern = re.compile(r"[\d+\w+]")
		string_list = pattern.findall(for_str)
		string = "".join(string_list)
		if code_type == self.code_type['order']:
			# return re.sub(r"PO", '', string)
			return string
		if code_type == self.code_type['track']:
			return string[0:12]
			# flag = re.search(r'#|=', string)
			# if flag:
			# 	string_cut_start = flag.span()[0]
			# 	return string[0:string_cut_start]
			# else:
			# 	return string

