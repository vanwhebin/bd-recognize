# _*_ coding: utf-8 _*_
# @Time     :   2020/7/14 19:06
# @Author       vanwhebin

from huey import crontab
from huey.contrib.djhuey import db_periodic_task
# from huey.contrib.djhuey import periodic_task, task
from django.db import connection
from utils.bi.spider import DataSpider
from bi.models import ProductSaleDetail, Brand, SalesTeam


@db_periodic_task(crontab(minute='1', hour='1'))
def update_sale_team():
	spider = DataSpider()
	groups = spider.get_sales_group()
	obj_list = []
	for group in groups:
		obj = SalesTeam(
			brand=group[0],
			name=group[1],
			manager=group[2],
			members=(group[2] + ', ' + group[3]),
		)
		obj_list.append(obj)
	cursor = connection.cursor()
	cursor.execute("TRUNCATE TABLE `bi_salesteam`")
	SalesTeam.objects.bulk_create(obj_list)


@db_periodic_task(crontab(minute='1', hour='1'))
def update_sale_detail():
	spider = DataSpider()
	sales_info = spider.get_sales_info()
	obj_list = []
	# cursor = connection.cursor()
	# cursor.execute("TRUNCATE TABLE `bi_productsaledetail`")
	for i in sales_info['data']:
		i['inventory'] = str(i['inventory'])
		obj = ProductSaleDetail(
			category=i['category'],
			amazon_id=i['amazon_id'],
			amazon_name=i['amazon_name'],
			asin=i['asin'],
			asin_url=i['asin_url'],
			sell_sku=i['sell_sku'],
			product_name=i['product_name'],
			ed_sku=i['ed_sku'],
			team_id=i['team_id'],
			team_name=i['team_name'],
			team_user=i['team_user'],
			team_username=i['team_username'],
			dev_team_id=i['dev_team_id'],
			dev_team_name=i['dev_team_name'],
			develop_user=i['develop_user'],
			develop_username=i['develop_username'],
			fba_qty=i['fba_qty'],
			fba_sell_qty=i['fba_sell_qty'],
			fba_unsell_qty=i['fba_unsell_qty'],
			fba_reserved_qty=i['fba_reserved_qty'],
			turn_days=i['turn_days'],
			total_qty=i['total_qty'],
			inventory=i['inventory'],
			order_qty=i['order_qty'],
			refund_qty=i['refund_qty'],
			orders=i['orders'],
			price=i['price'],
			refund=i['refund'],
			fee=i['fee'],
			freight=i['freight'],
			storage_charges=i['storage_charges'],
			advertising_fee=i['advertising_fee'],
			lightning_deals=i['lightning_deals'],
			evaluation_refund=i['evaluation_refund'],
			first_leg=i['first_leg'],
			transport_fee=i['transport_fee'],
			purchase_cost=i['purchase_cost'],
			gross_profit=i['gross_profit'],
			compensate=i['compensate'],
			tax_fee=i['tax_fee'],
			fixed_cost=i['fixed_cost'],
			ams_ads_fee=i['ams_ads_fee'],
			level=i['level'],
			level_txt=i['level_txt'],
		)
		if len(obj_list) % 200 == 0:
			ProductSaleDetail.objects.bulk_create(obj_list)
			obj_list = []
		obj_list.append(obj)
	ProductSaleDetail.objects.bulk_create(obj_list)


@db_periodic_task(crontab(minute='1', hour='1'))
def update_sale_brand():
	spider = DataSpider()
	brands = spider.get_brands()
	obj_list = []
	cursor = connection.cursor()
	cursor.execute("TRUNCATE TABLE `bi_brand`")
	for brand in brands:
		obj_list.append(Brand(name=brand))
	Brand.objects.bulk_create(obj_list)
	return True

# @huey.task(retries=2, retry_delay=60)
# def flaky_task(url):
#     This task might fail, in which case it will be retried up to 2 times
#     with a delay of 60s between retries.
# return this_might_fail(url)

