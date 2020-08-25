import json

from django.db import models
from django.utils import timezone


class SalesTeam(models.Model):
	def __str__(self):
		return self.name

	brand = models.CharField(max_length=255, default="", verbose_name="分组所属品牌")
	name = models.CharField(max_length=255, default="", verbose_name="分组名称")
	manager = models.CharField(max_length=255, default="", verbose_name="小组组长")
	members = models.CharField(max_length=800, default="", verbose_name="小组成员")


class Brand(models.Model):
	def __str__(self):
		return self.name

	name = models.CharField(max_length=255, default="", verbose_name="组名")


class ProductSaleDetail(models.Model):

	def __str__(self):
		return self.team_username + ' sales info'

	advertising_fee = models.FloatField(verbose_name="广告费")
	amazon_id = models.PositiveIntegerField(verbose_name="亚马逊店铺ID")
	amazon_name = models.CharField(max_length=50, verbose_name="亚马逊店铺渠道")
	ams_ads_fee = models.FloatField(max_length=50, verbose_name="AMS广告费")
	asin = models.CharField(max_length=50, verbose_name="ASIN")
	asin_url = models.CharField(max_length=255, verbose_name="亚马逊产品链接")
	category = models.CharField(max_length=50, verbose_name="品类")
	compensate = models.FloatField(verbose_name="物料赔偿")
	dev_team_id = models.PositiveIntegerField(verbose_name="开发团队ID")
	dev_team_name = models.CharField(max_length=255, verbose_name="开发团队")
	develop_user = models.PositiveIntegerField(verbose_name="开发人员ID")
	develop_username = models.CharField(max_length=255, verbose_name="开发人员")
	ed_sku = models.CharField(max_length=100, verbose_name="E登SKU")
	evaluation_refund = models.FloatField(verbose_name="测评费用")
	fba_qty = models.PositiveIntegerField(verbose_name="FBA库存")
	fba_reserved_qty = models.PositiveIntegerField(verbose_name="FBA预留库存")
	fba_sell_qty = models.PositiveIntegerField(verbose_name="FBA可销售库存")
	fba_unsell_qty = models.PositiveIntegerField(verbose_name="FBA不可销售库存")
	fee = models.FloatField(verbose_name="费用")
	first_leg = models.FloatField(verbose_name="头程")
	fixed_cost = models.FloatField(verbose_name="固定成本")
	freight = models.FloatField(verbose_name="运费")
	gross_profit = models.FloatField(verbose_name="毛利")
	inventory = models.CharField(max_length=255, verbose_name="库存")
	level = models.PositiveSmallIntegerField(verbose_name="产品等级ID")
	level_txt = models.CharField(max_length=50, verbose_name="产品等级")
	lightning_deals = models.FloatField(verbose_name="秒杀活动订单")
	order_qty = models.PositiveIntegerField(verbose_name="订单产品数量")
	orders = models.PositiveIntegerField(verbose_name="订单数量")
	price = models.FloatField(verbose_name="订单金额")
	product_name = models.CharField(max_length=255, verbose_name="产品名称")
	purchase_cost = models.FloatField(verbose_name="采购成本")
	refund = models.FloatField(verbose_name="退款金额")
	refund_qty = models.PositiveIntegerField(verbose_name="退款数量")
	sell_sku = models.CharField(max_length=255, verbose_name="渠道销售SKU")
	storage_charges = models.FloatField(verbose_name="仓储费")
	tax_fee = models.FloatField(verbose_name="税费")
	team_id = models.PositiveIntegerField(verbose_name="销售小组ID")
	team_name = models.CharField(max_length=255, verbose_name="销售小组")
	team_user = models.PositiveIntegerField(verbose_name="销售ID")
	team_username = models.CharField(max_length=255, verbose_name="销售")
	total_qty = models.PositiveIntegerField(verbose_name="总数量")
	transport_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="转运费")
	turn_days = models.CharField(max_length=50, verbose_name="周转天数")
	create_time = models.DateTimeField(default=timezone.now)

	# def save(self, *args, **kargs):
	# 	self.inventory = json.loads(self.inventory)
	# 	super(ProductSaleDetail, self).save(*args, **kargs)


class Sales(models.Model):

	def __str__(self):
		return self.name

	name = models.CharField(max_length=80, default="", verbose_name="销售名")


class SaleTeamMember(models.Model):

	def __str__(self):
		return 'sales_team_relationship_' + str(self.team_id) + '_' + str(self.sales_id)

	team_id = models.PositiveIntegerField(verbose_name="销售团队ID")
	sales_id = models.PositiveIntegerField(verbose_name="销售用户ID")
	manager = models.PositiveSmallIntegerField(verbose_name="是否组长", default=0)
