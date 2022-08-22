#!/bin/bash

1. wget https://ftp.cubrid.org/CUBRID_Drivers/Python_Driver/9.3.0/Linux/cubrid-python-9.3.0.0001.tar.gz
2. tar xvfz cubrid-python-9.3.0.0001.tar.gz
3. cd RB-9.3.0
4. CUBRIDdb/cursor.py
    def __del__(self):
        try:
            if self._cs:
                self.close()
        except AttributeError:   # self._cs not exists
            pass
5. python setup.py build
6. python setup.py install
