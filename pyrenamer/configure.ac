###################################
### Initialization
###################################
AC_INIT([pyrenamer], [0.4])
AC_CONFIG_SRCDIR(src/pyrenamer)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE


###################################
### Python modules
###################################
AM_PATH_PYTHON
PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)


###################################
### GConf
###################################
PKG_CHECK_MODULES(gconf, gconf-2.0)
AM_GCONF_SOURCE_2
AC_PATH_PROG([GCONFTOOL], [gconftool-2], [no])
if test "$GCONFTOOL" = "no"; then
	AC_MSG_ERROR([gconftool-2 not found])
fi


###################################
### Internationalization
###################################
GETTEXT_PACKAGE=pyrenamer
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])


###################################
### Check for eyeD3 (Music rename)
###################################
AC_MSG_CHECKING([for eyeD3 module])
if AC_RUN_LOG([DISPLAY= $PYTHON -c '
try:
    import eyeD3
except ImportError, e:
    if str(e).find("eyeD3") >= 0:
          raise
except:
    pass
']); then
  AC_MSG_RESULT([yes])
  HAVE_EYED3=True
else
  AC_MSG_RESULT([no])
  AC_MSG_WARN([eyeD3 not found, rename music disabled!])
  HAVE_EYED3=False
fi
AC_SUBST(HAVE_EYED3)


###################################
### Some variables
###################################
dnl if test "${prefix}" != NONE; then
dnl	RESOURCEDIR=${prefix}/share/$PACKAGE/
dnl	AC_SUBST(RESOURCEDIR)

dnl 	BINDIR=${prefix}/bin/
dnl	AC_SUBST(BINDIR)
dnl fi


###################################
### Config and output
###################################
AC_CONFIG_FILES([
	Makefile
	data/Makefile
	data/pyrenamer.desktop.in.in
	doc/Makefile
	images/Makefile
	po/Makefile.in
	src/Makefile
])
AC_OUTPUT