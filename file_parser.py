 
import sys
import numpy as np

import os
import shutil
from zipfile import ZipFile
from os import path
from shutil import make_archive

from tcms_lib import *

gSeparate = "======"


def parser_file(fname):
	with open(fname) as f:
		content = f.readlines()
	parser_content(content)
	#print content

def parser_content(content):
	subline = []
	info = {'Overview' : "", 'Toolchain supported' : "", 
	        'Hardware requirements': "", 'Board settings': "",
	        'Prepare the Demo': "", 'Running the demo':"",
	        'Customization options': ""}
	for i, item in enumerate(content):
		if gSeparate in item:
			subline.insert(len(subline), i + 1)
	if len(subline) == 0:
		print('\tnot a valid application readme')
		return None
	a = np.array(subline)
	#print(a)
	subline.pop(0)
	subline.insert(len(subline), len(content) + 2)
	b = np.array(subline)
	#print(b)
	c= np.column_stack((a, b - 2))
	#print(c)
	for ll in c:
		#print("\t*" + content[ll[0] - 2] + "*")
		info[content[ll[0] - 2].strip()] = '</p><p>'.join(content[ll[0]:ll[1]])
		#print(content[ll[0]:ll[1]])
	return info

def get_info(fn):
	info = {}
	ci = fn.split('/')
	#print(ci)
	if "boards" in ci:
		bi = ci.index('boards')
		info['platform'] = ci[bi + 1]
		info['catalogy'] = ci[bi + 2]
	if "readme.txt" in ci:
		bi = ci.index('readme.txt')
		if bi > 4:
			info['case_name'] =  '_'.join([ci[bi - 2], ci[bi - 1]])
		else:
			info['case_name'] = ci[bi - 1]
	#print("----\t" + str(info))
	return info

def parser_zip(zip_file):
	archive = ZipFile(zip_file, "r")
	rpc_client = connect()
	zfn = os.path.basename(zip_file)
	pvalues = {
	'product': 'MCU_SDK',
	'name': os.path.splitext(zfn)[0],
	'type': 'Function',
	'default_product_version': 'TEST_EAR',
	'text':'Test Plan for' + os.path.splitext(zfn)[0], 
	}
	p = creat_plan(rpc_client,pvalues)
	for fn in archive.namelist():
		if "readme.txt" in fn:
			info  = get_info(fn)
			bfread = archive.read(fn)
			fread = bfread.decode("utf-8")
			#print(bfread.decode("utf-8").split('\n'))
			info_plus = parser_content(fread.split('\n'))
			if info_plus and 'platform' in info:
				#print("----\t"+ str(info_plus))
				values = {
				'category': {'name': info['catalogy']},
				'product': {'name': 'MCU_SDK'},
				'summary': info['case_name'],
				'priority': 1,
				'estimated_time' : "00:00:05",
				}
				chash = {
				'product': 'MCU_SDK',
				'description' : "SDK",
				'name'        : info['platform']
			    }
				create_component(rpc_client ,chash)
				print(values)
				cs = create_case_with_componet(rpc_client, values, info['platform'])
				uhash = {
				'setup' : str(info_plus['Customization options']) + "\n" + str(info_plus['Hardware requirements'])
				+ "\n" + str(info_plus['Board settings']),
				'breakdown' : str(info_plus['Overview']) + "\n" +  str(info_plus['Prepare the Demo'])
				+ "\n" + str(info_plus['Toolchain supported']),
				'action' : str(info_plus['Running the demo']),
				'effect' : str(info_plus['Running the demo']),
				}
				try:
					res = update_case(rpc_client, cs['case_id'], uhash)
				except:
					print(uhash)
					
				add_case_to_plan(rpc_client, str(p['plan_id']), cs['case_id'])
				#print(res)
	confirm_plan(rpc_client, str(p['plan_id']))

				




def test_file_separate(fn):
	stl = parser_file(fn)
	print(stl)

def test_zip(fn):
	parser_zip(fn)


if __name__ == "__main__":
	print(sys.argv[1])
	#test_file_separate("./readme.txt")
	test_zip(sys.argv[1])



