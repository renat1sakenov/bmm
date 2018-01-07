#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
import time
from bs4 import BeautifulSoup


def export(efile):
	def new_folder(name,toolbar=0):
		return ('<DT><H3>'+name+'</H3>\n<DL><p>\n' if (toolbar == 0) else '<DT><H3 PERSONAL_TOOLBAR_FOLDER=\"true\">'+name+'</H3>\n<DL><p>\n')

	def new_item(link,ad,lm,title):
		return '<DT><A HREF="'+link+'" ADD_DATE="'+str(ad)+'" LAST_MODIFIED="'+str(lm)+'">'+title+'</A>\n'

	close_folder = "</DL><p>\n"

	try:
		export_file = open(efile,"w+")
	except:
		print("No such directory")
		sys.exit()	
	
	header = """<!DOCTYPE NETSCAPE-Bookmark-file-1>\r
		<!-- This is an automatically generated file.\r
		It will be read and overwritten.\r
		DO NOT EDIT! -->\r
		<META HTTP-EQUIV=\"Content-Type\"
		CONTENT=\"text/html; charset=UTF-8\">\r
		<TITLE>Bookmarks</TITLE>\r
		<H1>Bookmarks</H1>\r
		<DL><p>\r"""
	content = ""	
	
	counter = 0
	cs = (TOPLEVEL,0)
	old_cs = (TOPLEVEL,0)
	while counter < folder_id:	
		empty = False
		c.execute("SELECT folder.name,link,added,last_modified,title,toolbar FROM item,folder WHERE folder.id = item.folder AND folder.id="+str(counter))
		r = c.fetchall()
		
		if len(r) == 0:
			c.execute("SELECT folder.name,toolbar FROM folder WHERE folder.id ="+str(counter))
			r = c.fetchall()
			empty = True	
		cs = ((r[0][0].split(SEP)[-1],len(r[0][0].split(SEP)))) 
		#if one folder has finished (but the same superfolder continues), add closing tags.
		if int(cs[1]) < int(old_cs[1]):
			content += close_folder
		#if one folder has finished, and another different folder continues (superfolder has closed), add closing tags aswell.
		if int(cs[1]) <= int(old_cs[1]) and cs[0] != old_cs[0]:
			content += close_folder
		if counter != 0: 
			content += new_folder(cs[0],int(r[0][-1]))
		if not empty:
			for line in r:
				content += new_item(line[1],line[2],line[3],line[4])
		old_cs = cs
		counter+=1
	i = old_cs[1]
	while i > 0:
		content += close_folder
		i-=1
	content += "</DL>"
	export_file.write(header+content)
	export_file.close()


def print_all():

	def gs(l1,l2):
		return ''.join((1+l1-l2)*[" "])

	def gtime(val):
		if val == -1:
			return "NaN"
		return time.strftime('%Y-%m-%d %H:%M',time.gmtime(val))
	
	c.execute("SELECT item.id, folder.name, title, link, last_modified, added FROM folder, item  WHERE folder.id = item.folder")
	r = c.fetchall()

	if len(r) == 0:
		return

	print("print bookmarks")
	maxLen = [0,0,0]
	for line in r:
		for i in range(1,4):
			if i == 1:
				maxLen[0] = max(len(line[i])-len(TOPLEVEL),maxLen[0])
			else:
				maxLen[i-1] = max(len(line[i]),maxLen[i-1])
	header = "ID    FOLDER" + gs(maxLen[0],6) + "TITLE" + gs(maxLen[1],5) + "LINK" + gs(maxLen[2],4) + "LAST MODIFIED        ADDED"
	print(header)
	print(''.join(len(header)*["-"]))
	for line in r:
		folder = line[1].replace(SEP,"/")
		folder = folder.replace(TOPLEVEL+"/","")
		print(str(line[0]) + gs(4,0) + folder + gs(maxLen[0],len(folder)) + line[2] + gs(maxLen[1],len(line[2]))+ line[3] + gs(maxLen[2],len(line[3]))+ gtime(line[4]) + gs(4,0) + gtime(line[5]))



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

	TOOLBAR = "personal_toolbar_folder"
	LASTMOD = "last_modified"
	ADDDATE = "add_date"	

	argument_parser = argparse.ArgumentParser(description='Bookmark Manager.')
	argument_parser.add_argument('-i',action='store',dest='input_file',metavar='input file',help='import bookmark file')
	argument_parser.add_argument('-e',action='store',dest='output_file',metavar='output file',help='export bookmark file')
	argument_parser.add_argument('-p',action='store_true',help='print all bookmarks')
	argument_parser.add_argument('-D',action='store_true',help='remove all bookmarks')
	args = argument_parser.parse_args()

	if not os.path.exists(DIR):
		os.mkdir(DIR)
	try:
		info_file = open(INFO_PATH,"r")
		info_content = info_file.readlines()
		if len(info_content) != 0:
			item_id = int(info_content[0])
			folder_id = int(info_content[1])
		info_file.close()
	except:
		pass	


	con = sqlite3.connect(DB_PATH)
	c = con.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS item (id INT PRIMARY KEY NOT NULL, folder INT, link VARCHAR(100), added INT, last_modified INT, title VARCHAR(100), FOREIGN KEY(folder) REFERENCES folder(id)) ')
	c.execute('CREATE TABLE IF NOT EXISTS folder (id INT PRIMARY KEY, name VARCHAR(100), toolbar INT)')
	c.execute('SELECT name FROM folder WHERE name = \"'+TOPLEVEL+'\"')
	if c.fetchone() == None:
		c.execute('INSERT INTO folder VALUES (0,\"'+TOPLEVEL+'\",0)')		
	con.commit()

	# read input file
	if args.input_file != None:
		try:
			bookmarkfile = open(args.input_file,"r")
		except:
			print("File '" + args.input_file +"' not found!")
			sys.exit()
		if bookmarkfile.readline() == DOCTYPE:
			
			c.execute('SELECT name FROM folder')
			folder_res = str(c.fetchall())

			bs = BeautifulSoup(bookmarkfile,'html.parser')
			bs = str(bs)
			for elem in to_remove_tags:
				bs = bs.replace(elem,"")
			bs = BeautifulSoup(bs,'html.parser')
	
			try:
				folders = bs.find(FOLDER_BODY).descendants
			except:
				print("Invalid or empty file")
				sys.exit() 
		
			folder_list = {}
			for x in folders:
				if x.name == FOLDER_BODY and x.find_previous_sibling(H3_TAG) != None:
					s = ""
					p = x.parent
					tb = 0
					fname = x.find_previous_sibling().get_text()
					if x.find_previous_sibling().has_attr(TOOLBAR):
						tb  = 1
					s += fname
					while p.name != DOC_TAG:
						if p.name == FOLDER_BODY and p.find_previous_sibling(H3_TAG) != None:
							s =  p.find_previous_sibling(H3_TAG).get_text() +SEP+s
						p = p.parent	
					s = TOPLEVEL+SEP+s
					if "('"+s+"',)" not in folder_res:
						folder_list[fname] = folder_id
						c.execute('INSERT INTO folder VALUES (?,?,?)',(str(folder_id),s,tb))
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
					lm = ad = -1
					while p.name != FOLDER_BODY  and p.name != DOC_TAG:	
						p = p.parent
					if p.name != DOC_TAG:		
						folder_fk = folder_list[p.find_previous_sibling(H3_TAG).get_text()]
					if x.has_attr(LASTMOD):
						lm = x[LASTMOD]
					if x.has_attr(ADDDATE):
						ad = x[ADDDATE]
					txt = x.get_text().replace('"','\"')
					c.execute('INSERT INTO item VALUES (?,?,?,?,?,?)',(str(item_id),str(folder_fk),x['href'],str(ad),str(lm),txt))
					item_id += 1
			con.commit()
				
			info_file = open(INFO_PATH,"w+")
			info_file.write(str(item_id)+"\n"+str(folder_id)+"\n")	
			info_file.close()
		else:
			print("Not a bookmarkfile!")
			sys.exit()
	# export file
	elif args.output_file != None:
		export(args.output_file) 
	# print bookmarks
	elif args.p:
		print_all()
	elif args.D:
		try:
			os.remove(DB_PATH)
			os.remove(INFO_PATH)
			print("all bookmarks removed")
		except OSError as err:
			print(err)
	else:
		argument_parser.print_help()
