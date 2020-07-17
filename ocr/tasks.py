# _*_ coding: utf-8 _*_
# @Time     :   2020/7/14 19:06
# @Author       vanwhebin

from huey.contrib.djhuey import db_task, task

from ocr.utils.clip_pdf import ClipPDF


@db_task()
def recognize(db_items):
	clip = ClipPDF()
	clip.run(db_items)
	return True


@task()
def add_num(a, b):
	print(a)
	print(b)
	return a + b


# @huey.task(retries=2, retry_delay=60)
# def flaky_task(url):
#     This task might fail, in which case it will be retried up to 2 times
#     with a delay of 60s between retries.
# return this_might_fail(url)


# @huey.periodic_task(crontab(minute='0', hour='3'))
# def nightly_backup():
#     sync_all_data()
