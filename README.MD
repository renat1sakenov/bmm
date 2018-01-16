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
-i FILE

		import html file into the database. 
		Duplicates won't be stored.
		Folders with same path will be merged.

-e FILE 	

		Export database as html file

-p [KEYWORD | title=KEYWORD | link=KEYWORD | folder=KEYWORD]

		Print all bookmarks that match the keyword (regex expression).
		With no argument, all bookmarks will be printed.
        searching can be limited with "title=","link=" and "folder=" prefixes

-d KEYWORD ( KEYWORD| title=KEYWORD | link=KEYWORD | folder=KEYWORD )
		
		deletes all bookmarks matching keyword (regex expression) according to prefix.

-D		

		delete all bookmarks

-h 

		print help

-n		

		print number of bookmarks and folders		
	
```
