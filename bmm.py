#!/usr/bin/python3
import sys
import argparse
import sqlite3
import getpass
import os
import time
import re
import json
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

	recently_bookmarked = "<DT><A HREF=place:folder=BOOKMARKS_MENU&folder=UNFILED_BOOKMARKS&folder=TOOLBAR&queryType=1&sort=12&maxResults=10&excludeQueries=1>Recently bookmarked</A>\n"
	
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
			if len(r) == 0:
				counter+=1 
				continue
			empty = True	
		cs = ((r[0][0].split(SEP)[-1],len(r[0][0].split(SEP)))) 
		#if one folder has finished (but the same superfolder continues), add closing tags.
		
		if int(cs[1]) < int(old_cs[1]):
			i = 0
			diff = int(old_cs[1]) - int(cs[1]) + 1
			for i in range(diff):	
				content += close_folder
		if int(cs[1]) == int(old_cs[1]) and cs[0] != old_cs[0]:
			content += close_folder 

		#if one folder has finished, and another different folder continues (superfolder has closed), add closing tags aswell.
		#if int(cs[1]) <= int(old_cs[1]) and cs[0] != old_cs[0]:
		#	content += close_folder
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
	export_file.write(header+recently_bookmarked+content)
	export_file.close()

def searchterm_result(search = None):
	if not search: 
		c.execute(DEFAULT_ITEM_QUERY)
	else:
		search_args = search.split("=")
		
		if len(search_args) > 2:
			return None

		if len(search_args) == 1:
			c.execute(DEFAULT_ITEM_QUERY + " AND (title REGEXP ? OR link REGEXP ? OR folder.name REGEXP ?)",(search,search,search))
		elif search_args[0] == 'title':
			c.execute(DEFAULT_ITEM_QUERY + " AND title REGEXP ?",(str(search_args[1]),))
		elif search_args[0] == 'link':
			c.execute(DEFAULT_ITEM_QUERY + " AND link REGEXP ?",(str(search_args[1]),))
		elif search_args[0] == 'folder':
			c.execute(DEFAULT_ITEM_QUERY + " AND folder.name REGEXP ?",(str(search_args[1]),))
		else:
			return None

	r = c.fetchall()
	return r

def query_result(query):
	if not query:
		return None
	else:
		c.execute(DEFAULT_ITEM_QUERY + query)
	r = c.fetchall()
	return r

def print_result(r):

	def gtime(val):
		if val == -1:
			return "NaN"
		return time.strftime('%Y-%m-%d %H:%M',time.gmtime(val))

	if r == None or len(r) == 0:
		print("No bookmarks found.")
		return

	for line in r:
		folder = line[1].replace(SEP,"/")
		folder = folder.replace(TOPLEVEL+"/","")
		print(str(line[0]) + ": " + line[2] + "\n" + line[3] + "\n" + folder + " | LM: " + str(gtime(line[4])) + " | A: " + str(gtime(line[5]))+  "\n")

def delete(search):
		
	def check_for_empty_folders():
		c.execute("SELECT id FROM folder")
		fids = c.fetchall()
		for fid in fids:
			c.execute("SELECT item.id FROM item, folder WHERE item.folder="+str(fid[0]))
			if c.fetchone() == None:
				c.execute("DELETE FROM folder WHERE id ="+str(fid[0]))
		con.commit()

	r = searchterm_result(search)
	if r == None or len(r) == 0:
		print("No matching bookmarks found")
		return
	print_result(r)
	while True:
		answer = input("Are you sure you want to delete these bookmarks? (y/n) ")
		if answer == 'y':
			
			search_args = search.split("=")
			if len(search_args) == 1:
				c.execute("DELETE FROM item WHERE title REGEXP ? OR link REGEXP ? OR folder IN (SELECT id FROM folder WHERE folder.name REGEXP ?)",(search,search,search))
			elif search_args[0] == "title":
				c.execute("DELETE FROM item WHERE title REGEXP ?",(str(search_args[1]),))
			elif search_args[0] == "link":
				c.execute("DELETE FROM item WHERE link REGEXP ?",(str(search_args[1]),))
			elif search_args[0] == "folder":
				c.execute("DELETE FROM item WHERE folder IN (SELECT id FROM folder WHERE folder.name REGEXP ?)",(str(search_args[1]),))
				c.execute("DELETE FROM folder WHERE name REGEXP ?",(str(search_args[1]),))
		
			con.commit()	
			check_for_empty_folders()	
			print("bookmarks deleted")
			return
		elif answer == 'n':
			return

def print_number():
	c.execute('SELECT COUNT(id) FROM item')
	count_items  = c.fetchone()[0]
	c.execute('SELECT COUNT(id) FROM folder')
	count_folder = c.fetchone()[0]
	print(str(count_items) + " bookmarks, " + str(count_folder) + " folders")


def regexp(expr,item):
	reg = re.compile(expr)
	return reg.search(item) is not None

def print_latest(num):
	if not num.isdigit():
		print("argument must be an integer!")
		return
	if int(num) > int(c.execute("SELECT COUNT(id) FROM item").fetchone()[0]):
		print("argument not in valid range.")
		return
	c.execute(DEFAULT_ITEM_QUERY + " ORDER BY item.added DESC LIMIT " + str(num))
	print_result(c.fetchall())

def write_info():
	info_file = open(INFO_PATH,"w+")
	info_file.write(str(item_id)+"\n"+str(folder_id)+"\n")	
	info_file.close()

if __name__ == "__main__":
	DOCTYPE = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
	TOPLEVEL = "BMM_TOPLEVEL"
	DIR = os.path.expanduser("~") + "/.bmm/"
	DB_PATH = DIR + "db"
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

	SMART_BOOKMARK_TAG = "place:"
	JSON_TOOLBAR = "toolbar_____"
	DEFAULT_ITEM_QUERY = "SELECT item.id, folder.name, title, link, last_modified, added FROM folder, item  WHERE folder.id = item.folder "

	VERSION = "1.0"

	h1 = """print bookmarks matching to the expression.
    	expression can be: exp | title=exp | link=exp | folder=exp. No argument: print everything."""

	h2 = """delete all bookmarks matching the expression.
		 expression can be: exp | title=exp | link=exp"""

	argument_parser = argparse.ArgumentParser(description='A simple application to import, merge, print and export bookmarks.')
	argument_parser.add_argument('-i','--import',action='store',dest='input_file',metavar='input file',help='import bookmark file')
	argument_parser.add_argument('-e','--export',action='store',dest='output_file',metavar='output file',help='export bookmark file')
	argument_parser.add_argument('-p','--print',action='store',dest='print_param',metavar='expression',nargs='?',const='*',help= h1)
	argument_parser.add_argument('-D',action='store_true',help='remove all bookmarks')
	argument_parser.add_argument('-d','--delete',action='store',dest='delete_param',metavar='expression',nargs=1,help= h2)
	argument_parser.add_argument('-n','--numbers',action='store_true',dest='num',help='print total number of folders and bookmarks')
	argument_parser.add_argument('-l','--latest',action='store',dest='latest_num',metavar='num',nargs='?',const='10',help='print the last num bookmarks')
	argument_parser.add_argument('-a','--add',action='store',dest='add_bm',metavar="bookmark",help="Add a bookmark (title,url,path)")
	argument_parser.add_argument('-v','--version',action='store_true',help="print version")
	args = argument_parser.parse_args()

	if not os.path.exists(DIR):
		os.mkdir(DIR)
	os.system("touch "+ INFO_PATH)
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
	c.execute('CREATE TABLE IF NOT EXISTS item (id INT PRIMARY KEY NOT NULL, folder INT, link VARCHAR(250), added INT, last_modified INT, title VARCHAR(250), FOREIGN KEY(folder) REFERENCES folder(id)) ')
	c.execute('CREATE TABLE IF NOT EXISTS folder (id INT PRIMARY KEY, name VARCHAR(250), toolbar INT)')
	c.execute('SELECT name FROM folder WHERE name = \"'+TOPLEVEL+'\"')
	if c.fetchone() == None:
		c.execute('INSERT INTO folder VALUES (0,\"'+TOPLEVEL+'\",0)')		
	con.create_function("REGEXP",2,regexp)
	con.commit()

	os.chmod(DB_PATH,0o640)
	os.chmod(INFO_PATH,0o640)
	
	# read input file
	if args.input_file != None:
		try:
			bookmarkfile = open(args.input_file,"r")
		except:
			print("File '" + args.input_file +"' not found!")
			sys.exit()
		start_pos = bookmarkfile.tell()

		c.execute('SELECT name FROM folder')
		folder_res = str(c.fetchall())

		c.execute('SELECT link FROM item')
		link_res = str(c.fetchall())

		#counter just for user information
		folder_counter = 0
		item_counter = 0
		folder_list = {}

		if bookmarkfile.readline() == DOCTYPE:
			try:
				bs = BeautifulSoup(bookmarkfile,'html.parser')
				bs = str(bs)
				for elem in to_remove_tags:
					bs = bs.replace(elem,"")
				bs = BeautifulSoup(bs,'html.parser')
	
				folders = bs.find(FOLDER_BODY).descendants
			except:
				print("Invalid or empty file")
				sys.exit() 

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
						folder_counter += 1
					else:
						c.execute('SELECT id FROM folder WHERE name="'+s+'"')
						folder_list[fname] = int(c.fetchone()[0])
			con.commit()
			folder_res = None

			links = bs.find_all(LINK_TAG)
			for x in links:
				if "('"+x['href']+"',)" not in link_res and "(\""+x['href']+"\",)" not in link_res and not x['href'].startswith(SMART_BOOKMARK_TAG):
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
					item_counter += 1
			con.commit()
		else:
			bookmarkfile.seek(start_pos)
			try:
				json_content = json.load(bookmarkfile)
			except:
				print("Not a bookmarkfile!")
				sys.exit()

			def json_bookmark_parser(json_content,folders):
				global folder_id,folder_counter,c, item_id, item_counter, folder_list
				title = None
				if "children" in json_content:
					for x in json_content["children"]:
						if "uri" not in x:
							tb = 0
							title = folders + SEP + x["title"]
							if title not in folder_res:
								if JSON_TOOLBAR in x["guid"]:
									tb = 1
								c.execute('INSERT INTO folder VALUES (?,?,?)',(str(folder_id),str(title),tb))	
								folder_list[title] = folder_id
								folder_id += 1
								folder_counter += 1
						json_bookmark_parser(x,(title if (title !=  None) else folders))
				else:
					try:
						link = json_content["uri"]
						if link not in link_res and folders != None:
							title = json_content["title"]
							ad = json_content["dateAdded"]
							lm = json_content["lastModified"]
							folder_fk = folder_list[folders]
							c.execute('INSERT INTO item VALUES (?,?,?,?,?,?)',(str(item_id),str(folder_fk),link,ad,lm,title))	
							item_counter += 1
							item_id += 1
					except Exception as err:
						pass

			json_bookmark_parser(json_content,TOPLEVEL)
			con.commit()	
				
		print("Added "+str(folder_counter)+" new folders and "+str(item_counter)+" new bookmarks.")
		write_info()
	elif args.output_file != None:
		export(args.output_file) 
	elif args.print_param != None:
		if args.print_param == '*':
			print_result(searchterm_result())
		else:
			print_result(searchterm_result(args.print_param))	
	elif args.D:
		try:
			os.remove(DB_PATH)
			os.remove(INFO_PATH)
			print("all bookmarks removed")
		except OSError as err:
			print(err)
	elif args.delete_param != None:
			delete(args.delete_param[0])
	elif args.num:
		print_number()
	elif args.latest_num:
		print_latest(args.latest_num)
	elif args.add_bm != None:
		params = args.add_bm.split(",")
		if len(params) != 3:
			print("Could not add bookmark. Provide the bookmark in comma-separated list (title,url,path) e.g.: 'test','example.com',bookmarks/important'")
			sys.exit(1)
		title = params[0]
		url = params[1]
		path = TOPLEVEL + SEP + params[2].replace("/",SEP)
		ad = lm = time.time()

		c.execute("SELECT id FROM item WHERE link='"+url+"'")
		if c.fetchone() != None:
			print("bookmark already exists")
			sys.exit(0)

		c.execute("SELECT id FROM folder WHERE name = '"+path+"'")
		try:
			res = c.fetchone()[0]
		except:
			c.execute('INSERT INTO folder VALUES (?,?,?)',(str(folder_id),path,0))
			con.commit()
			res = folder_id
			folder_id += 1
		c.execute('INSERT INTO item VALUES (?,?,?,?,?,?)',(str(item_id),str(res),url,ad,lm,title))	
		con.commit()
		item_id += 1
		write_info()
		print("bookmark added")
	elif args.version:
		print(VERSION)
	else:
		argument_parser.print_help()
