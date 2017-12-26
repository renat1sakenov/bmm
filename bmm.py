#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
from bs4 import BeautifulSoup


	
def export_file(efile):
	pass
	

def print_all():
	print("print all")
	c.execute("SELECT * FROM folder")
	r = c.fetchall()
	for line in r:
		print(line)

	print("------------------------")
	c.execute("SELECT * FROM item")
	r = c.fetchall()
	for line in r:
		print(line)	

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
	LINK_TAG = "a"
	DOC_TAG = "[document]"
	SEP = "_._"
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
	c.execute('CREATE TABLE IF NOT EXISTS item (id INT PRIMARY KEY NOT NULL, folder INT, link VARCHAR(100), added INT, last_modfied INT, title VARCHAR(100), FOREIGN KEY(folder) REFERENCES folder(id)) ')
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
			

			c.execute('SELECT name FROM folder')
			folder_res = str(c.fetchall())


			bs = BeautifulSoup(bookmarkfile,'html.parser')
			bs = str(bs)
			for elem in to_remove_tags:
				bs = bs.replace(elem,"")
			bs = BeautifulSoup(bs,'html.parser')
			folders = bs.find(FOLDER_BODY).descendants
	
			folder_list = {}
			for x in folders:
				if x.name == FOLDER_BODY and x.find_previous_sibling(H3_TAG) != None:
					s = ""
					p = x.parent
					fname = x.find_previous_sibling().get_text()
					s += fname
					while p.name != DOC_TAG:
						if p.name == FOLDER_BODY and p.find_previous_sibling(H3_TAG) != None:
							s =  p.find_previous_sibling(H3_TAG).get_text() +SEP+s
						p = p.parent	
					if "('"+s+"',)" not in folder_res:
						folder_list[fname] = folder_id
						c.execute('INSERT INTO folder VALUES ('+str(folder_id)+',"'+s+'")')
						folder_id += 1
					else:
						c.execute('SELECT id FROM folder WHERE name="'+s+'"')
						folder_list[fname] = int(c.fetchone()[0])
			con.commit()
			folder_res = None

			c.execute('SELECT link FROM item')
			link_res = str(c.fetchall())

			links = bs.find_all(LINK_TAG)
			for x in links:
				if "('"+x['href']+"',)" not in link_res and "place:folder" not in x['href']: #testing for now
					folder_fk = 0	
					p = x.parent
					while p.find_previous_sibling(H3_TAG) == None and  p.name != DOC_TAG:	#wrong: does not find correct parent	
						p = p.parent
					if p.name != DOC_TAG:		
						folder_fk = folder_list[p.find_previous_sibling(H3_TAG).get_text()]
					
					print(str(item_id) + " " + str(folder_fk) + " " + x['href'] + " " + x['add_date'] + " " + x['last_modified'] + " " + x.get_text())
					c.execute('INSERT INTO item VALUES ('+str(item_id)+','+str(folder_fk)+',"'+x['href']+'",'+x['add_date']+','+x['last_modified']+',"'+x.get_text()+'")')
					item_id += 1
			con.commit()
					
			
			


			#todo: write to db_index
			
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
