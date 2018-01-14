DIR = $(DESTDIR)/usr/local/bin

install:
	install -m755 -d $(DIR)
	install -m755 bmm.py $(DIR)/bmm

uninstall:
	rm -f $(DIR)/bmm
