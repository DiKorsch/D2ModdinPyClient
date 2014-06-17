# D2ModdinPyClient

Crossplatform equivalence to https://github.com/kidovate/D2ModdinClient

[![Build Status](https://travis-ci.org/BloodyD/D2ModdinPyClient.svg)](https://travis-ci.org/BloodyD/D2ModdinPyClient)

## Tested with:
  - python 2.7
  - PyQt 4.8

## How to start develop

### Clone and install dependecies
``` 
cd ~
git clone https://github.com/BloodyD/D2ModdinPyClient.git d2modd
cd d2modd
chmod +x install_deps.sh install_sip.sh install_pyqt.sh
./install_deps.sh
virtualenv .
source bin/activate
pip install -r requirements.txt
./install_sip.sh
./install_pyqt.sh

```

### Run tests
```
cd ~/d2modd/tests
python runner.py
```

### Run client
```
cd ~/d2modd/src
python main.py
```



## How to deploy

### Windows
```
cd ~/d2modd/src
pyinstaller windows.spec
```
binaries are located in `~/d2modd/src/dist/d2mpclient/`

### Linux


### Mac



