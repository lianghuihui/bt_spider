bt_spider - just a toy spider
=============================

Installation / Usage
--------------------

    $ git clone git@github.com:lianghuihui/bt_spider.git
    $ cd bt_spider
    $ virtualenv .venv
    $ . .venv/bin/activate
    $ pip install -r requirements.txt

and run 

    $ python bt_spider.py | tee rst.log

and using shell to show the top 50 movices

    $ less rst.log | grep '<===>' | awk -F '<===>' '{print $4"  "$3"  "$2"  "$5}' | LC_ALL=C sort -k 1,2 -r | head -n 50

enjoy
