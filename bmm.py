#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
from bs4 import BeautifulSoup

def write_to_db():
	pass

	
def export_file(efile):
	pass
	

def print_all():
	print("print all")
	print(DIR)


if __name__ == "__main__":
	DOCTYPE = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
	TOPLEVEL = "BMM_TOPLEVEL"
	USER = getpass.getuser()
	DIR = "/home/"+USER+"/.bmm/"
	DB_PATH = DIR + "db"
	#write current item and folders max id into db_index
	INFO_PATH = DIR + "db_index" 	
	c = None
	con = None
	info_file = None
	item_id = 0
	folder_id = 1

	FOLDER_TAG = "dt"
	H3_TAG = "h3"
	FOLDER_BODY = "dl"
	DOC_TAG = "[document]"
	to_remove_tags = ['<dd>']

	argument_parser = argparse.ArgumentParser(description='Bookmark Manager.')
	argument_parser.add_argument('-i',action='store',dest='input_file',metavar='input file',help='import bookmark file')
	argument_parser.add_argument('-e',action='store',dest='output_file',metavar='output file',help='export bookmark file')
	argument_parser.add_argument('-p',action='store_true',help='print all bookmarks')
	args = argument_parser.parse_args()

	if not os.path.exists(DIR):
		os.mkdir(DIR)

	info_file = open(INFO_PATH,"w+")
	info_content = info_file.readlines()
	if len(info_content) != 0:
		item_id = int(info_content[0])
		folder_id = int(info_content[1])

	con = sqlite3.connect(DB_PATH)
	c = con.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS item (id INT PRIMARY KEY NOT NULL, folder INT, link VARCHAR(100), added INT, last_modfied INT, description VARCHAR(1000), FOREIGN KEY(folder) REFERENCES folder(id)) ')
	c.execute('CREATE TABLE IF NOT EXISTS folder (id INT PRIMARY KEY, name VARCHAR(100))')
	c.execute('SELECT name FROM folder WHERE name = \"'+TOPLEVEL+'\"')
	if c.fetchone() == None:
		c.execute('INSERT INTO folder VALUES (0,\"'+TOPLEVEL+'\")')		
	con.commit()


	# read input file
	if args.input_file != None:
		try:
			bookmarkfile = open(args.input_file,"r")
		except:
			print("File '" + args.input_file +"' not found!")
			sys.exit()
		if bookmarkfile.readline() == DOCTYPE:
			#import_file	

			bs = BeautifulSoup(bookmarkfile,'html.parser')
			bs = str(bs)
			for elem in to_remove_tags:
				bs = bs.replace(elem,"")
			bs = BeautifulSoup(bs,'html.parser')
			content = bs.find(FOLDER_BODY).descendants

			l = []
			for x in content:
				if x.name == FOLDER_BODY and x.find_previous_sibling(H3_TAG) != None:
					s = ""
					p = x.parent
					s += x.find_previous_sibling().get_text()
					while p.name != DOC_TAG:
						if p.name == FOLDER_BODY and p.find_previous_sibling(H3_TAG) != None:
							s =  p.find_previous_sibling(H3_TAG).get_text() +"/"+s
						p = p.parent	
					l.append(s)
			print(l)	#l containing all folders in hierarchy
		else:
			print("Not a bookmarkfile!")
			sys.exit()
	# export file
	elif args.output_file != None:
		export_file(args.output_file)
	# print bookmarks
	elif args.p:
		print_all()
	else:
		argument_parser.print_help()
