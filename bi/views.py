from django.db import transaction
from django.http import JsonResponse
from django.db import connection

from utils.bi.spider import DataSpider
from bi.models import ProductSaleDetail, Brand, SalesTeam, Sales, SaleTeamMember


def sales_data(request):
	spider = DataSpider()
	sales_info = spider.get_sales_info()
	obj_list = []
	cursor = connection.cursor()
	cursor.execute("TRUNCATE TABLE `bi_productsaledetail`")
	# ProductSaleDetail.objects.all().delete()
	# with open("sales_data.json", 'w') as f:
	# 	f.write(json.dumps(sales_info['data'], sort_keys=True, indent=4))
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
	return JsonResponse({"data": sales_info})


def sales_brand(request):
	spider = DataSpider()
	_request = spider.login()
	brands = spider.get_brands()
	for brand in brands:
		Brand.objects.create(name=brand)
	return JsonResponse({"data": brands})


def sales_team(request):
	spider = DataSpider()
	groups = spider.get_sales_group()

	cursor = connection.cursor()
	cursor.execute("TRUNCATE TABLE `bi_salesteam`")
	sales_set = set()
	sales_obj_dict = {}

	with transaction.atomic():
		save_id = transaction.savepoint()

		try:
			for group in groups:
				group_obj = SalesTeam.objects.create(
					brand=group[0],
					name=group[1],
					manager=group[2],
					members=(group[2] + ', ' + group[3]),
				)
				sales_list = group_obj.members.split(', ')
				for sales in sales_list:
					if sales not in sales_set:
						sales_set.add(sales)
						sales_obj = Sales.objects.create(name=sales)
						sales_obj_dict[sales] = sales_obj.id

					SaleTeamMember.objects.create(
						team_id=group_obj.id,
						sales_id=sales_obj_dict[sales]
					)

			# 处理其他两个表
		except Exception as e:
			print(e.args)
			obj_list = []
			transaction.savepoint_rollback(save_id)
			for group in groups:
				obj = SalesTeam(
					brand=group[0],
					name=group[1],
					manager=group[2],
					members=(group[2] + ', ' + group[3]),
				)
				obj_list.append(obj)
			SalesTeam.objects.bulk_create(obj_list)

			return False
		# 提交订单成功，显式的提交一次事务
		transaction.savepoint_commit(save_id)

	return JsonResponse({"data": groups})
