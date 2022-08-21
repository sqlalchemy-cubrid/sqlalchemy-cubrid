#!/bin/bash

curl https://ftp.cubrid.org/CUBRID_Drivers/Python_Driver/11.1.0/Linux/cubrid-python-11.1-latest.tar.gz --output cubrid-python.tar.gz
tar xvfz cubrid-python.tar.gz
cd RB-11.1.0
python setup.py build
python setup.py install
