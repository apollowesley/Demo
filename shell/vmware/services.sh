#!/bin/sh

export PATH=/sbin:/bin

log() {
   echo "$*"
   logger init "$*"
}

statusChange() {
   log $*
   esxcfg-init --set-boot-status-text "$*"
   esxcfg-init --set-boot-progress step
}

# Try esxcli to set firewall first. If return value is not 0,
# that demonstrates hostd is not up, yet. Then try localcli,
# which always succeeds. Setting firewall in this way,
# guarantees new settings sync to hostd cache.
update_ruleset_status() {
   /sbin/esxcli network firewall ruleset set -r $1 -e $2
   if [ $? -ne 0 ]; then
      /sbin/localcli network firewall ruleset set -r $1 -e $2
   fi
}

update_firewall() {
   if [ $1 = "ntpd" ]; then
      update_ruleset_status "ntpClient" $2
   elif [ $1 = "SSH" ]; then
      update_ruleset_status "sshServer" $2
   elif [ $1 = "vpxa" ]; then
      update_ruleset_status "vpxHeartbeats" $2
   elif [ $1 = "sfcbd-watchdog" ]; then
      update_ruleset_status "CIMHttpServer" $2
      update_ruleset_status "CIMHttpsServer" $2
   fi
}

start_svc() { 
   service=$1
   log "services.sh: start $service"
   dir=`dirname $service`
   svc=`basename $service`
   statusChange "Running $svc start"
   cd $dir
   update_firewall $svc true
   $service start
   log "services.sh: started $service"
}

stop_svc() { 
   service=$1
   log "services.sh: stop $service"
   dir=`dirname $service`
   svc=`basename $service`
   statusChange "Running $svc stop"
   cd $dir
   $service stop
   update_firewall $svc false
   log "services.sh: stopped $service"
}

start() {
   esxcfg-init --set-boot-progress-text "Starting up services"
   ulimit -s 512
   svclsts=`/sbin/chkconfig -iom`

   cmdline=$(/bin/bootOption -roC)
   
   if echo $cmdline | grep -q -e '\<services.sequential\>' ; then
      mode=sequential
   else
      mode=parallel
   fi
   
   # service lists (all services of one start priority) are separated by \n
   IFS=$'\n'
   for svclst in $svclsts; do
      # services in a list are separated by \t
      IFS=$'\t'
      for service in $svclst; do
         if [ -x "$service" ]; then
            if [ $mode == "sequential" ]; then
               start_svc $service
            else
               start_svc $service &
            fi
         fi
      done

      # Wait for all services of this set to start
      wait
   done
}

stop() {
   startdir=`pwd`
   svclst=`/sbin/chkconfig -o | sed -n -e '1!G' -e 'h' -e '$p'`
   for service in $svclst; do
      if [ -x "$service" ]; then
         stop_svc $service
      fi
   done

   # Wait for all services to stop
   wait 

   cd $startdir
}

action=$1
case "$1" in
   start)
      start
      ;;
   stop)
      stop
      ;;
   restart)
      stop
      start
      ;;
   *)
      echo "Usage: `basename "$0"` {start|stop|restart}"
      exit 1
esac

