#!/bin/bash
rm -rf ./dumpdata/
mkdir dumpdata
./dump_uline.sh
./dump_uline_trade.sh
chown -R deploy:deploy ./dumpdata
