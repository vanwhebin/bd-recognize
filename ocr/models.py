import os
from django.db import models
from djangodir.settings import MEDIA_PATH


class Invoice(models.Model):

	def __str__(self):
		return self.file_type + '_' + self.title

	file_type = models.CharField(max_length=50, default="", verbose_name="单据类型")
	title = models.CharField(max_length=100, default="", verbose_name="单据名称")
	order_num = models.CharField(max_length=50, default="", verbose_name="订单号")
	tracking_num = models.CharField(max_length=50, default="", verbose_name="物流跟踪号")
	# hash = models.CharField(max_length=32, default="", verbose_name="文件hash值", db_index=True)
	location = models.CharField(max_length=255, default="", verbose_name="文件保存位置")
	create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

	def get_absolute_url(self):
		return os.path.join(MEDIA_PATH, self.location)
