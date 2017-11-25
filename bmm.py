#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
from bs4 import BeautifulSoup

DOCTYPE = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
USER = getpass.getuser()
DIR = "/home/"+USER+"/.bmm/"
DB_PATH = DIR + "db"

def main():
	argument_parser = argparse.ArgumentParser(description='Bookmark Manager.')
	argument_parser.add_argument('-i',action='store',dest='input_file',metavar='input file',help='import bookmark file')
	argument_parser.add_argument('-e',action='store',dest='output_file',metavar='output file',help='export bookmark file')
	argument_parser.add_argument('-p',action='store_true',help='print all bookmarks')
	args = argument_parser.parse_args()

	# read input file
	if args.input_file != None:
		try:
			bookmarkfile = open(args.input_file,"r")
		except:
			print("File '" + args.input_file +"' not found!")
			return	
		if bookmarkfile.readline() == DOCTYPE:
			import_file(bookmarkfile)
		else:
			print("Not a bookmarkfile!")
			return
	# export file
	elif args.output_file != None:
		pass
	# print bookmarks
	elif args.p:
		print_all()
	else:
		argument_parser.print_help()


#return the bookmarks database
def load_db(): 
		if not os.path.exists(DIR):
			os.mkdir(DIR)
		con = sqlite3.connect(DB_PATH)
		cursor = con.cursor()
		''' ... '''
		con.commit()
		con.close()

def write_to_db():
	pass

def import_file(ifile):
	bs = BeautifulSoup(ifile,'html.parser')
	
def export_file(efile):
	pass

def print_all():
	print("print all")
	print(DIR)
	load_db()

if __name__ == "__main__":
	main()
