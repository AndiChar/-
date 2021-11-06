#!/usr/bin/python3
from pdf2image import convert_from_path
import os
import sys
from PIL import Image
import cv2
import numpy as np
import pytesseract
import re
from pytesseract import image_to_string
import requests
import time

def shablon(content):
	print('''
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<style type="text/css">
			html, body { height:100%; margin:0px; padding:0px; } 
		</style> 
		<link rel="stylesheet" href="/style.css">
		<script type="text/javascript" src="/jquery-3.3.1.min.js"></script>
		<script type="text/javascript" src="/script.js"></script>
		<title>UAI Team</title>
	</head>
	<body>
		<table border="0" align="center" width="100%" height="100%" cellspacing="0">
			<tr height="40" >
				<td width="7%" rowspan="4" bgcolor="#D0D0D0"></td>
				<td bgcolor="#CC2222">
					<table style="color: white; padding:0px 30px; font-size: 18px;">
						<tr>
							<td><img src="https://www.mos.ru/front/markup/header-footer/media/small-logo.7260e7ff.svg" alt="" aria-hidden="true" align="left"></td>
							<!-- <td>&nbsp;&nbsp;mos.ru</td> -->
							<td>&nbsp;&nbsp;Решение от команды UAI Team</td>
						</tr>
					</table>
				</td>
				<td width="7%" rowspan="4" bgcolor="#D0D0D0"></td>
			</tr>
			<tr height="55" >
				<td style="border-bottom: 1px solid #D0D0D0; padding:0px 30px; font-size: 24px; text-align: center;">Сервис по обезличиванию персональных данных в документах</td>
			</tr>
			<tr>
				<td>
					<table border="0" cellspacing="0" align="center">
						<tr>
							<td align="center">''' + content + '''
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td>
				</td>
			</tr>
		</table>
	</body>
</html>'''
	 )

#фунция конвертации doc в pdf
def convert_doc_to_pdf(file_path):
	w_dir = os.getcwd()
	f_dir = '/'.join(file_path.split('/')[:-1])
	f_name = file_path.split('/')[-1]
	os.chdir(f_dir)
	cmd = f'libreoffice --convert-to pdf "{f_name}"'
	os.system(cmd)
	os.chdir(w_dir)
	f_name = '.'.join(f_name.split('.')[:-1]) + '.pdf'
	return f_name

def save_img(l, FOLDER_JPG, file_info):
	for i in enumerate(l):
		n = str(i[0])
		if len(n) < 3:
			n = '0'*(3-len(n)) + n
		i[1].save(os.path.join(FOLDER_JPG, '.'.join(file_info[:-1])+'___'+n+'.jpg'),'JPEG')

def Recognize_and_depersonalize(path_doc):
	img = cv2.imread(path_doc)
	img2 = img.copy()
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	data = pytesseract.image_to_data(img, lang='rus')
	k = 0
	text = ''
	dictWord = {}
	dataT = data.splitlines()[1:]
	n = 0
	for i, el in enumerate(dataT):
		el = el.split()
		try:
			if len(el[11]) > 2: el[11] = re.sub("[.|;|,|/]","", el[11])
			if n == el[2]:
				text += el[11]+' '
			else:
				text += ', ' + el[11]+' '
			dictWord[el[11]]=i
			n = el[2]
		except:
			k += 1
			continue
	r_pavlov = requests.post('http://127.0.0.1:5005/model', json={"x": [text.split(' ')]})
	pavlov_answer = r_pavlov.json()
	pavlov_answer = pavlov_answer[0]
	named_words = []
	for i in range(len(pavlov_answer[0])):
		if 'PER' in pavlov_answer[1][i]:
			named_words.append(pavlov_answer[0][i])
	img3 = img2.copy()
	for el in dataT:
		el = el.split()
		txt = el[-1]
		if txt == '-1': continue
		for pers in named_words:
			for i_pers in pers.split():
				if i_pers.strip() in txt.strip():
					x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])
					ROI = img3[y - 3:y + h + 3, x-5:x+w+5]
					blur = cv2.GaussianBlur(ROI, (15, 15), 0)
					img3[y-3:y+h+3, x-5:x+w+5] = blur
					shum = np.full(ROI.shape, (127,127,127))
					img3[y-3:y+h+3, x-5:x+w+5] = shum
	return img3, named_words

def jpg2pdf(folder_jpg, user_id, f_name):
	f_l = os.listdir(folder_jpg)
	f_l = [i for i in f_l if str(user_id) in i]
	f_l.sort()
	jpegslist = []
	k = 0
	for i in f_l:
		convertjpeg = Image.open(os.path.join(folder_jpg, i))
		x = convertjpeg.convert('RGB')
		jpegslist.append(x)
	if len(f_l) > 1:
		jpegslist[0].save(os.path.join(folder_jpg, f_name+'.pdf'), save_all=True, append_images=jpegslist[1:])
	else:
		jpegslist[0].save(os.path.join(folder_jpg, f_name+'.pdf'))
	return f_name

def create_download_page(f_name, found_text):
	n_row = len(found_text)
	table_f = ''
	if found_text:
		table_f = '''<table border="0">'''
		for i in found_text:
			table_f += '''<tr><td>&nbsp;&nbsp;<label><input type="checkbox"/>&nbsp;&nbsp;'''+i+'''</label></td></tr>'''
		table_f += '''</table>'''
	table_content = '''<table cellspacing="0"  height="100%" width="100%"><tr><td  height="100%" width="86%"><iframe src="/out/'''+ f_name +'''.pdf"  height="100%" width="100%"></iframe></td><td>''' + table_f + '''</td></tr></table>'''
	h = '''
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<link rel="stylesheet" href="/style.css">
		<script type="text/javascript" src="/jquery-3.3.1.min.js"></script>
		<script type="text/javascript" src="/script.js"></script>
		<title>UAI Team</title>
	</head>
	<body>
		<table border="0" align="center" height="100%" width="100%" cellspacing="0">
			<tr height="40" >
				<td width="7%" rowspan="4" bgcolor="#D0D0D0"></td>
				<td bgcolor="#CC2222">
					<table style="color: white; padding:0px 30px; font-size: 18px;">
						<tr>
							<td><img src="https://www.mos.ru/front/markup/header-footer/media/small-logo.7260e7ff.svg" alt="" aria-hidden="true" align="left"></td>
							<!-- <td>&nbsp;&nbsp;mos.ru</td> -->
							<td>&nbsp;&nbsp;Решение от команды UAI Team</td>
						</tr>
					</table>
				</td>
				<td width="7%" rowspan="4" bgcolor="#D0D0D0"></td>
			</tr>
			<tr height="55" >
				<td style="border-bottom: 1px solid #D0D0D0; padding:0px 30px; font-size: 24px; text-align: center;">Сервис по обезличиванию персональных данных в документах</td>
			</tr>
			<tr height="100%" width="86%">
				<td  height="100%" width="86%">
					<table border="0" cellspacing="0" align="center" height="100%" width="100%">
						<tr>
							<td align="center" width="100%">
								<a href="/out/'''+f_name+'''.pdf" download>Скачать файл</a>
								<br><br>
								<a href="http://62.84.122.231">Обработать еще файл</a>
								<br><br>
							</td>
							<tr><td align="left" height="100%" width="86%">''' + table_content + '''</td></tr>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td>
				</td>
			</tr>
		</table>
	</body>
</html>'''
	with open('/home/g_user/dowload.html', 'w') as f:
		f.write(h)
