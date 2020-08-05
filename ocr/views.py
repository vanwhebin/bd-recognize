# _*_ coding: utf-8 _*_
# @Time     :   2020/7/9 15:41
# @Author       vanwhebin
import os
import time
import hashlib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from .models import Invoice
from djangodir.settings import MEDIA_ROOT
from ocr.utils.clip_pdf import ClipPDF
from ocr.tasks import recognize


@csrf_exempt
def invoice(request):
	res_list = []
	data = []
	response = {'code': 200, 'msg': '', "data": []}
	if request.method == "POST":
		# 处理上传文件
		clip = ClipPDF()
		uploaded_files = handle_upload(request)
		# 识别invoice
		data = clip.check_multi_page(uploaded_files)
		# if len(data) > 10:
		# 为防止每个任务http连接太长被远程服务器强制断开，将任务处理的列表切片
		# clip_list = handle_cli_list(data, 10)
		for clip in data:
			recognize([clip])
		response['msg'] = "上传票据成功，识别中"
		# 返回结果 根据上传文件的标题查找数据库信息，返回结果
	elif request.method == "GET":
		file_id = request.GET.get('id', '')
		if not file_id:
			raise RuntimeError('请提供正确的ID')
		ids = list(set(file_id.split(',')))
		data = Invoice.objects.filter(id__in=ids)
		response['msg'] = "OK"
	for obj in data:
		dict_obj = model_to_dict(obj)
		dict_obj['location'] = obj.get_absolute_url()
		res_list.append(dict_obj)
	# 格式化返回
	response['data'] = res_list
	return JsonResponse(response)


def handle_cli_list(full_list, per_list_len):
	""" 将整个list按数量切片为多个列表"""
	list_of_group = zip(*(iter(full_list),) * per_list_len)
	end_list = [list(i) for i in list_of_group]  # i is a tuple
	count = len(full_list) % per_list_len
	end_list.append(full_list[-count:]) if count != 0 else end_list
	return end_list


@csrf_exempt
def rerun(request):
	""" 重新执行任务 """
	res_list = []
	response = {'code': 200, 'msg': '', "data": []}
	if request.method == "POST":
		file_id = request.POST.get('id', '')
		if not file_id:
			raise RuntimeError('请提供正确的ID')
		ids = list(set(file_id.split(',')))
		data = Invoice.objects.filter(id__in=ids)
		response['msg'] = "OK"
		for clip in data:
			recognize([clip])
			dict_obj = model_to_dict(clip)
			dict_obj['location'] = clip.get_absolute_url()
			res_list.append(dict_obj)
		response['msg'] = "任务再次执行"
		# 格式化返回
		response['data'] = res_list
		return JsonResponse(response)


def handle_upload(request):
	uploaded_file = request.FILES.getlist('file')

	if not uploaded_file:
		raise Exception(msg=u"没有文件上传或非法数据")
	else:
		time_tag = time.strftime('%Y-%m-%d')
		dir_path = os.path.join(MEDIA_ROOT, time_tag)
		upload_files = []
		for it in uploaded_file:
			file_name = it.name.replace('"', '')
			if not os.path.exists(dir_path):
				os.makedirs(dir_path)
			with open(os.path.join(dir_path, file_name), 'wb') as f:
				file_content = it.read()
				f.write(file_content)
				inv = Invoice.objects.create(location=os.path.join(time_tag, file_name), title=file_name)
				upload_files.append(inv)

		return upload_files

