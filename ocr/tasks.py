# _*_ coding: utf-8 _*_
# @Time     :   2020/7/14 19:06
# @Author       vanwhebin

from huey.contrib.djhuey import db_task, task

from ocr.utils.clip_pdf import ClipPDF


@db_task(retries=1, retry_delay=1)
def recognize(db_items):
	clip = ClipPDF()
	clip.save_log("start_time: " + clip.get_time())
	clip.run(db_items)
	clip.save_log("end_time: " + clip.get_time())
	return True
