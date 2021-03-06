# bmm - Bookmark Manager

## Description

bmm is a python script which lets you import and export bookmark.html files.  
Commandline tool for Linux.

## Installation

Clone or download this repository and run `sudo make install`.     
To uninstall run `sudo make uninstall`.

## Dependencies:

- Python3
- beautifulsoup4

## Usage

```
-i FILE, --import FILE  

		import html/json file into the database. 
		Duplicates won't be stored.
		Folders with same path will be merged.

-e FILE, --export FILE   	

		Export database as html file

-p EXP, --print EXP

		Print all bookmarks that match the expression.
		With no argument, all bookmarks will be printed.
		Can be used with title=EXP, link=EXP, folder=EXP
		Example: bmm -p link=youtube

-d EXP, --delete EXP
		
		deletes all bookmarks matching expression.  
		Can be used with title=EXP, link=EXP, folder=EXP  
		Example: bmm -d folder="trash bin"  

-D 		

		delete all bookmarks

-h, --help   

		print help

-n, --numbers  		

		print number of bookmarks and folders  

-l [NUM], --latest [NUM]  
   
		print the latest added NUM bookmarks. Default is 10.  

-a title,url,path , --add title,url,path

		add a new bookmark using a comma-separated list  
		example: bmm -a testname,https://www.example.com,Bookmarks/Important
	
```
