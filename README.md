# What's RYU-OE
######RYU-OE(RYU Optical Extension) is an OpenFlow Controller which can support OTN(Optical Transport Network). New OTN parameters are added in Match Fields of OpenFlow Protocol ver1.3.
The detail of the extended OpenFlow specification is to be published by ONF in near future.

# Quick Start
Installing Ryu is::

   $ git clone https://github.com/o3project/ryu-oe.git
   $ cd ryu-oe
   $ sudo python ./setup.py install

if ryu-oe REST API use::

   $ cd ryu/app/
   $ ryu-manager ./ofctl_rest.py
