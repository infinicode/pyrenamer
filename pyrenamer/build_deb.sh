#! /bin/sh

mkdir deb
cp debian/changelog debian.changelog

make distclean
./autogen.sh
dch --newversion 0.3+svn`date +%G%m%d`-0ubuntu1 "New version from SVN"
dpkg-buildpackage -rfakeroot -us -uc

mv ../pyrenamer_0.3+svn* deb/
mv deb/ ~/pyrenamer-deb
rm debian/changelog
mv debian.changelog debian/changelog

fakeroot ./debian/rules clean
