Desktopdir = $(datadir)/applications
Desktop_in_files = pyrenamer.desktop.in
Desktop_DATA = $(Desktop_in_files:.desktop.in=.desktop)
$(Desktop_in_files): $(Desktop_in_files:.desktop.in=.desktop.in.in)
@INTLTOOL_DESKTOP_RULE@

schemasdir = $(GCONF_SCHEMA_FILE_DIR)
schemas_in_files = pyrenamer.schemas.in
schemas_DATA = $(schemas_in_files:.schemas.in=.schemas)
@INTLTOOL_SCHEMAS_RULE@

if GCONF_SCHEMAS_INSTALL
install-data-local: install-schemas
install-schemas:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(schemas_DATA)
endif

gladedir = $(RESOURCEDIR)
glade_DATA = pyrenamer.glade

DISTCLEANFILES =                \
	$(schemas_DATA)		\
	$(Desktop_DATA)
	
EXTRA_DIST =  			\
	$(glade_DATA)		\
	$(schemas_in_files) 	\
	$(Desktop_in_files)	\
	$(Desktop_DATA)
