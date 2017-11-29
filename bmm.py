#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
from bs4 import BeautifulSoup

def write_to_db():
	pass

def import_file(ifile):
	
	#test
	c.execute('SELECT * FROM folder')
	print(c.fetchall())
	#testend

	bs = BeautifulSoup(ifile,'html.parser')
	list_folders = bs.find_all('h3')
	#go through all subfolders 
	for elem in list_folders:
		n = elem.get_text()
		c.execute('SELECT name FROM folder WHERE name = \"'+n+'\"')
		#if the subfolder does not exist, create it in db
		if c.fetchone() == None:
			c.execute('INSERT INTO folder (name) VALUES (\"'+n+'\")')  
			con.commit()
	
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

	argument_parser = argparse.ArgumentParser(description='Bookmark Manager.')
	argument_parser.add_argument('-i',action='store',dest='input_file',metavar='input file',help='import bookmark file')
	argument_parser.add_argument('-e',action='store',dest='output_file',metavar='output file',help='export bookmark file')
	argument_parser.add_argument('-p',action='store_true',help='print all bookmarks')
	args = argument_parser.parse_args()

	if not os.path.exists(DIR):
		os.mkdir(DIR)
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
			import_file(bookmarkfile)
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
