# What's RYU-OE
"Opt-transport apps of O3 orchestrator&amp;controller suite"
---
RYU-OE(RYU Optical Extension) is an OpenFlow Controller which can support OTN(Optical Transport Network). New OTN parameters are added in Match Fields of OpenFlow Protocol ver1.3.
The detail of the extended OpenFlow specification is to be published by ONF in near future.


 Build
--------------------------

    $ cd ~
    $ git clone https://github.com/o3project/ryu-oe.git
    $ sudo python ~/ryu-oe/setup.py install


 Starting RYU-OE
--------------------------

    $ cd ~/ryu-oe/ryu/app
    $ ryu-manager ./ofctl_rest.py

 Stopping RYU-OE
--------------------------
   
    Press Ctrl+C.
