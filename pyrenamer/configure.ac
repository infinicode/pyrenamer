AC_INIT(src/pyrenamer)

PACKAGE=pyrenamer
VERSION=0.1

AM_INIT_AUTOMAKE($PACKAGE, $VERSION)
AM_MAINTAINER_MODE


AM_PATH_PYTHON
PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)

PKG_CHECK_MODULES(GCONF, gconf-2.0)
AC_PATH_PROG(GCONFTOOL, gconftool-2)
AM_GCONF_SOURCE_2


BINDIR=${prefix}/bin
AC_SUBST(BINDIR)

IMAGEDIR=${prefix}/share/$PACKAGE
AC_SUBST(IMAGEDIR)

RESOURCEDIR=${prefix}/share/$PACKAGE
AC_SUBST(RESOURCEDIR)


AC_OUTPUT([
Makefile
src/Makefile
src/pyrenamer_globals.py
data/Makefile
data/pyrenamer.desktop
data/pyrenamer.schemas
doc/Makefile
images/Makefile
])
