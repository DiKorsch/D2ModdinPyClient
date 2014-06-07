sudo apt-get install python-qt4
cd ..
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16/sip-4.16.tar.gz
tar -xvf sip-4.16.tar.gz
cd sip-4.16
python configure.py
make
sudo make install
cd ..
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11/PyQt-x11-gpl-4.11.tar.gz
tar -xvf PyQt-x11-gpl-4.11.tar.gz
cd PyQt-x11-gpl-4.11
python configure-ng.py --confirm-license -e QtCore -e QtGui -e QtNetwork
make
sudo make install