# What's RYU-OE
"Opt-transport apps of O3 orchestrator&amp;controller suite"
---
RYU-OE is based on RYU V3.9 developed by NTT.  
In RYU-OE, some OTN parameters are added to the Match Fields of OpenFlow protocol (ver1.3) to support OTN. The detail of the extended OpenFlow specification is to be published by ONF in near future.　

Please see http://www.o3project.org/ja/fujitsu/docs/getting_started_OPT.pdf for detailed instructions of "Opt-transport apps of O3 orchestrator & controller suite". 

**Please also look at the Web page that easily explained our OSS (http://www.o3project.org/en/fujitsu/index.html)

* Build
--------------------------

    $ cd ~  
    
    $ git clone https://github.com/o3project/ryu-oe.git  
    
    $ cd ~/ryu-oe 
    
    $ sudo python ./setup.py install  




* Starting RYU-OE
--------------------------

    $ cd ~/ryu-oe/ryu/app
    
    $ ryu-manager ./ofctl_rest.py

* Stopping RYU-OE
--------------------------
   
    Press Ctrl+C.
