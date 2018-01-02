#!/bin/sh 
#
# Copyright 2008 VMware, Inc.  All rights reserved.
#
# host powerops:
#    Shutdown power operation for the host
#
#

# Default power operation
POWEROP="-s"

set_login_info() {
   /bin/ticket --reap
   TICKET=`/bin/ticket --generate`
   export CIM_HOST_USERID=$TICKET
   export CIM_HOST_PASSWD=$TICKET
}

apply_host_powerop() {
   cim_host_powerops $POWEROP
}

# all logging is done by host_powerops
set_login_info
apply_host_powerop

echo "Shutting Down..."
