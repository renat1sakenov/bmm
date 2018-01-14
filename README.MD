# bmm - Bookmark Manager

## Description

bmm is a python script which lets you import and export bookmark.html files.  
Cli tool for linux only (right now)

## Installation

Clone or download this repository and run `sudo make install`.     
To uninstall run `sudo make uninstall`.

## Dependencies:

- Python3
- beautifulsoup4

## Usage

```
-i FILE

		import file into the database. 
		Duplicates won't be stored.
		Folders with same path will be merged.

-e FILE 	

		Export database as html file

-p [keyword]

		Print all bookmarks that match the search term.
		With no argument, all bookmarks will be printed.

-d [KEYWORD | folder PATH]
		
		deletes all bookmarks matching keyword.
		If the first argument is "folder", it deletes the given folder 

-D		

		delete all bookmarks

-h 

		print help

-n		

		print number of bookmarks and folders		
	
```
