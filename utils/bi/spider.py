# _*_ coding: utf-8 _*_
# @Time     :   2020/8/21 15:02
# @Author       vanwhebin
import time
import json
import requests
from bs4 import BeautifulSoup
from .rsa_encrypt import Encrypt


class DataSpider:
	rsa_dir = 'libs/rsa'
	login_encrypt_key = ""
	login_dict = {
		"email": "wanweibin@aukeys.com",
		"password": 'wanweibin',
		"verifyCode": ""
	}
	urls = {
		"login": {"url": "http://sky.aukeyit.com/user/login", "method": "post", 'ajax': True},
		"logout": {"url": "http://sky.aukeyit.com/user/logout", "method": "get"},
		"sales_info": {"url": "http://sky.aukeyit.com/amazon/dashboard/trend-ajax", "method": "post", 'ajax': True},
		"sales_trend": {"url": "http://sky.aukeyit.com/amazon/dashboard/trend", "method": "get"},
		"group": {"url": "http://sky.aukeyit.com/amazon/team/index", "method": "get"},
		"product": {"url": "http://sky.aukeyit.com/amazon/product/download", "method": "get"},
		"listing": {"url": "http://sky.aukeyit.com/amazon/dashboard/listing-rank-ajax", "method": "get", 'ajax': True},
		"brand": {"url": "http://sky.aukeyit.com/amazon/brand/index", "method": "get"},
	}

	ajax_header = {'X-Requested-With': 'XMLHttpRequest'}
	csrf_header = {'X-CSRF-Token': ""}
	post_header = {'Content-Type': 'application/x-www-form-urlencoded'}

	headers = {
		'Referer': 'http://sky.aukeyit.com/user/login',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
		'Cookie': ""
	}

	sales_query_params = {
		"type": "",
		"startDate": "",
		"endDate": "",
		"amazonIds": "",
		"teamIds": "",
		"teamUserIds": "",
		"productName": "",
		"edSku": "",
		"asin": "",
		"devTeamIds": "",
		"developUserIds": "",
		"category": "",
		"level": "",
	}

	s = None

	def __init__(self):
		self.s = requests.session()
		login_status = self._check_login()
		if not login_status:
			self.login()

	def login(self):
		self._get_csrf_token()
		encrypt = Encrypt()
		self.login_dict['password'] = encrypt.get_rsa_pass(self.login_dict['password'])
		headers = {**self.headers, **self.post_header, **self.ajax_header, **self.csrf_header}
		login_res = self.s.post(self.urls['login']['url'], data=self.login_dict, headers=headers)
		if login_res.status_code == 200 or login_res.status_code == 302:
			print(u"登录成功" + str(login_res.status_code))
			self.headers['Cookie'] = '_identity=' + self.s.cookies['_identity'] + '&' + self.headers['Cookie']
			# print(self.s.headers)
			# print(self.s.cookies)
			return self.s
		else:
			return False

	def _get_request_cookies(self):
		""" 获取request请求会话中的cookie """
		cookies = requests.utils.dict_from_cookiejar(self.s.cookies)
		print(cookies)

	def _check_login(self):
		""" 检查是否已登录"""
		login_response = self.s.get(self.urls['login']['url'], headers=self.headers)
		if login_response.status_code == 302:
			return True
		else:
			return False

	def _get_csrf_token(self):
		login_page = self.s.get(self.urls['login']['url'], headers=self.headers)
		soup = BeautifulSoup(login_page.content, features='html.parser', from_encoding='utf-8')
		csrf_token = soup.head.find(attrs={"name": "csrf-token"}).get('content')
		self.csrf_header['X-CSRF-Token'] = csrf_token
		self.headers['Cookie'] = "_csrf=" + self.s.cookies['_csrf']

	def logout(self):
		return requests.get(self.urls['logout']['url'])

	def get_sales_info(self, **kwargs):
		# 销售明细
		if "startDate" not in kwargs:
			kwargs["startDate"] = time.strftime('%Y-%m-') + '1'
		if "endDate" not in kwargs:
			kwargs["endDate"] = time.strftime('%Y-%m-%d')
		data = {**self.sales_query_params, **kwargs}
		sales_info_res = self.s.post(
			self.urls['sales_info']['url'],
			data=data,
			headers={**self.s.headers, **self.ajax_header})
		if sales_info_res.status_code == 200:
			return json.loads(sales_info_res.content)
		else:
			return []

	def get_products_list(self):
		pass

	def get_sales_group(self):
		# 获取所有的销售小组和销售人员信息
		group_page = self.s.get(self.urls['group']['url'])
		table = []

		soup = BeautifulSoup(group_page.content, features='html.parser', from_encoding='utf-8')
		trs = soup.find(id="team_table_1").find("tbody").find_all('tr')
		for tr in trs:
			column = []
			tds = tr.find_all('td')
			for i in range(1, 5):
				column.append(str(tds[i].string or ''))
			table.append(column)
		return table

	def get_brands(self):
		# 获取所有的品牌分类信息
		brands = []
		brand_page = self.s.get(self.urls['brand']['url'])
		soup = BeautifulSoup(brand_page.content, features='html.parser', from_encoding='utf-8')
		brand_count = len(soup.find(id="w1").find_all('li')) - 2  # 去掉前一页和后一页
		if brand_count > 0:
			# 从第二页进行循环
			for page in range(1, (brand_count + 1)):
				brands.extend(self._get_brands(page))

		else:
			brands.extend(self._get_brands())
		return brands

	def _get_brands(self, page=1):
		# 返回一个品牌列表
		column = []
		brand_page = self.s.get(self.urls['brand']['url'] + f'?page={page}')
		soup = BeautifulSoup(brand_page.content, features='html.parser', from_encoding='utf-8')
		trs = soup.tbody.find_all("tr")
		for i in trs:
			column.append(i.find("td").next_sibling.string)
		return column
