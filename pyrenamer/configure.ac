AC_INIT(src/pyrenamer)

PACKAGE=pyrenamer
VERSION=0.2

AM_INIT_AUTOMAKE($PACKAGE, $VERSION)
AM_MAINTAINER_MODE

dnl -- Python modules
AM_PATH_PYTHON
PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)

dnl -- Gconf
PKG_CHECK_MODULES(GCONF, gconf-2.0)
AC_PATH_PROG(GCONFTOOL, gconftool-2)
AM_GCONF_SOURCE_2

dnl -- Check for eyeD3 (Music rename)
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

dnl -- Internationalization
AC_PROG_INTLTOOL([0.23])
ALL_LINGUAS="en es"
GETTEXT_PACKAGE=$PACKAGE
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT


dnl -- Some dir vars
BINDIR=${prefix}/bin
AC_SUBST(BINDIR)

IMAGEDIR=${prefix}/share/$PACKAGE
AC_SUBST(IMAGEDIR)

RESOURCEDIR=${prefix}/share/$PACKAGE
AC_SUBST(RESOURCEDIR)

LOCALEDIR=${prefix}/share/locale
AC_SUBST(LOCALEDIR)

AC_OUTPUT([
Makefile
src/Makefile
src/pyrenamer_globals.py
data/Makefile
data/pyrenamer.desktop.in
data/pyrenamer.schemas
doc/Makefile
images/Makefile
po/Makefile.in
])
