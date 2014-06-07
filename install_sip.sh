cd ..
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16/sip-4.16.tar.gz
tar -xvf sip-4.16.tar.gz
cd sip-4.16
python configure.py
make
sudo make install
