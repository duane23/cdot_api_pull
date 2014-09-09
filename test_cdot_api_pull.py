#!/usr/bin/python
##
## $Id$
##
## Todo:
##  - 
##
import sys,string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd
from CdotPerf import CdotPerf
from Daemon import Daemon
from cdot_api_pull import MyDaemon

def main():
    test = MyDaemon(Daemon)
    test.run()


if __name__ == "__main__":
    main()
    sys.exit(0)
