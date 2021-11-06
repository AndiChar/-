#!/usr/bin/python3
print('<!DOCTYPE html>')
from pdf2image import convert_from_path # библиотека для конвертирования pdf в jpeg
import os
import sys
from PIL import Image
import cgi, os
import cgitb; cgitb.enable()
import func_lib as fl
import cv2
import numpy as np
import pytesseract
import re
import time
from pytesseract import image_to_string

FOLDER_IN = '/home/g_user/in'
FOLDER_WORK = '/home/g_user/work'
FOLDER_OUT = '/home/g_user/out'

content = '''								<form id="upload-container" method="POST" action="/cgi-bin/index.py" enctype="multipart/form-data">
									<img id="upload-image" src="/upload.svg">
									<div>
										<input id="file-input" type="file" name="file">
										<label for="file-input">Выберите файл</label>
										<!-- <span>или перетащите его сюда</span> -->
									</div>
								</form>'''

form = cgi.FieldStorage()
user_id = str(int(time.time()*1000))
try:
	fileitem = form['file']
	if fileitem.file:
		f_name = os.path.basename(fileitem.filename.replace("\\", "/" ))
		f_name = f_name.split('.')
		if len(f_name) > 1:
			f_type = f_name[-1]
			f_name = '.'.join(f_name[:-1])+'_'+user_id
			open(FOLDER_IN + '/' + f_name + '.' + f_type, 'wb').write(fileitem.file.read())
			load_gif  = '<img id="load-image" src="/load.gif">'
			if len(os.listdir(FOLDER_IN)) != 0:
				file_to_convert = [i for i in os.listdir(FOLDER_IN) if user_id in i][0]
				file_info = file_to_convert.split('.')
				if f_type.lower() in ['pdf', 'pd']:
					pdf2jpeq = convert_from_path(os.path.join(FOLDER_IN, file_to_convert))
					fl.save_img(pdf2jpeq, FOLDER_WORK, file_info)
					fl.shablon(load_gif)
					for img_file in [i for i in os.listdir(FOLDER_WORK) if user_id in i]:
						rez_img, found_per = fl.Recognize_and_depersonalize(os.path.join(FOLDER_WORK, img_file))
						cv2.imwrite(os.path.join(FOLDER_OUT, img_file), rez_img)
					f_n_d = fl.jpg2pdf(FOLDER_OUT, user_id, f_name)
					fl.create_download_page(f_n_d, found_per)
					clear_in = '''find "'''+FOLDER_IN+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					clear_work = '''find "'''+FOLDER_WORK+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					os.system(clear_in)
					os.system(clear_work)
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/dowload.html"></head><body></body></html>
					''')
				elif f_type.lower() in ['doc', 'docx', 'xls', 'xlsx', 'do', 'xl', 'rtf']:
					file_to_convert = fl.convert_doc_to_pdf(os.path.join(FOLDER_IN, file_to_convert))
					pdf2jpeq = convert_from_path(os.path.join(FOLDER_IN, file_to_convert))
					fl.save_img(pdf2jpeq, FOLDER_WORK, file_info)
					fl.shablon(load_gif)
					for img_file in [i for i in os.listdir(FOLDER_WORK) if user_id in i]:
						rez_img, found_per = fl.Recognize_and_depersonalize(os.path.join(FOLDER_WORK, img_file))
						rez_img = Image.fromarray(rez_img.astype('uint8'))
						rez_img.save(os.path.join(FOLDER_OUT, img_file))
					f_n_d = fl.jpg2pdf(FOLDER_OUT, user_id, f_name)
					fl.create_download_page(f_n_d, found_per)
					clear_in = '''find "'''+FOLDER_IN+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					clear_work = '''find "'''+FOLDER_WORK+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					os.system(clear_in)
					os.system(clear_work)
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/dowload.html"></head><body></body></html>
					''')
				elif f_type.lower() in ['jpg', 'jpeg']:
					os.system(f'cp -r {FOLDER_IN}/*{user_id}* {FOLDER_WORK}')
					fl.shablon(load_gif)
					for img_file in [i for i in os.listdir(FOLDER_WORK) if user_id in i]:
						rez_img, found_per = fl.Recognize_and_depersonalize(os.path.join(FOLDER_WORK, img_file))
						rez_img = Image.fromarray(rez_img.astype('uint8'))
						rez_img.save(os.path.join(FOLDER_OUT, img_file))
					f_n_d = fl.jpg2pdf(FOLDER_OUT, user_id, f_name)
					fl.create_download_page(f_n_d, found_per)
					clear_in = '''find "'''+FOLDER_IN+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					clear_work = '''find "'''+FOLDER_WORK+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					os.system(clear_in)
					os.system(clear_work)
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/dowload.html"></head><body></body></html>
					''')
				elif f_type.lower() in ['zip']:
					fl.shablon(load_gif)
					f_name_full = f_name+'.'+f_type
					unpack_cmd = f'unzip -qo "{os.path.join(FOLDER_IN, f_name_full)}" -d "{os.path.join(FOLDER_WORK, f_name)}"'
					os.system(unpack_cmd)
					a_1, a_2, a_3 = next(os.walk(os.path.join(FOLDER_WORK, f_name)))
					a_2 = a_2 + a_3
					f_per = []
					for i in a_2:
						if i.split('.')[-1].lower() in ['doc', 'docx', 'xls', 'xlsx', 'do', 'xl', 'rtf']:
							file_to_convert = fl.convert_doc_to_pdf(os.path.join(a_1, i))
					for i in os.listdir(a_1):
						if i.split('.')[-1].lower() in ['pdf', 'pd']:
							pdf2jpeq = convert_from_path(os.path.join(a_1, i))
							fl.save_img(pdf2jpeq, a_1, i.split('.'))
					for i in os.listdir(a_1):
						if i.split('.')[-1].lower() in ['jpg', 'jpeg']:
							rez_img, found_per = fl.Recognize_and_depersonalize(os.path.join(a_1, i))
							f_per += found_per
							rez_img = Image.fromarray(rez_img.astype('uint8'))
							rez_img.save(os.path.join(FOLDER_OUT, ''.join(i.split('.')[:-1])+'_'+user_id+'.jpg'))
					f_n_d = fl.jpg2pdf(FOLDER_OUT, user_id, f_name)
					fl.create_download_page(f_n_d, f_per)
					clear_in = '''find "'''+FOLDER_IN+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					clear_work = '''find "'''+FOLDER_WORK+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					os.system(clear_in)
					os.system(clear_work)
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/dowload.html"></head><body></body></html>
					''')
				elif f_type.lower() in ['rar']:
					fl.shablon(load_gif)
					f_name_full = f_name+'.'+f_type
					os.system(f'mkdir "{os.path.join(FOLDER_WORK, f_name)}"')
					unpack_cmd = f'unrar e -cl -y -c- "{os.path.join(FOLDER_IN, f_name_full)}"  "{os.path.join(FOLDER_WORK, f_name)}" &> None'
					os.system(unpack_cmd)
					a_1, a_2, a_3 = next(os.walk(os.path.join(FOLDER_WORK, f_name)))
					a_2 = a_2 + a_3
					f_per = []
					for i in a_2:
						if i.split('.')[-1].lower() in ['doc', 'docx', 'xls', 'xlsx', 'do', 'xl', 'rtf']:
							file_to_convert = fl.convert_doc_to_pdf(os.path.join(a_1, i))
					for i in os.listdir(a_1):
						if i.split('.')[-1].lower() in ['pdf', 'pd']:
							pdf2jpeq = convert_from_path(os.path.join(a_1, i))
							fl.save_img(pdf2jpeq, a_1, i.split('.'))
					for i in os.listdir(a_1):
						if i.split('.')[-1].lower() in ['jpg', 'jpeg']:
							print(i)
							rez_img, found_per = fl.Recognize_and_depersonalize(os.path.join(a_1, i))
							f_per += found_per
							rez_img = Image.fromarray(rez_img.astype('uint8'))
							rez_img.save(os.path.join(FOLDER_OUT, ''.join(i.split('.')[:-1])+'_'+user_id+'.jpg'))
					f_n_d = fl.jpg2pdf(FOLDER_OUT, user_id, f_name) ##
					fl.create_download_page(f_n_d, f_per)
					clear_in = '''find "'''+FOLDER_IN+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					clear_work = '''find "'''+FOLDER_WORK+'''" -type f -name "*'''+user_id+'''*" -exec rm -f {} \;'''
					os.system(clear_in)
					os.system(clear_work)
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/dowload.html"></head><body></body></html>
					'''
					)
				else:
					print('''
					<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/index.html"></head><body></body></html>
					''')
			else:
				print('''
				<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/index.html"></head><body></body></html>
				''')
		else:
			print('''
			<html><head><meta http-equiv="refresh" content="0; URL=http://62.84.122.231/index.html"></head><body></body></html>
			''')
except Exception as ex:
	fl.shablon(str(ex))
