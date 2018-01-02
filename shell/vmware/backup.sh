#!/bin/sh

. /etc/vmware/BootbankFunctions.sh

TRUE=0
FALSE=1

EXIT_SUCCESS=0
EXIT_FAILURE=1

LIVEINST_MARKER=/var/run/update_altbootbank

sysalert()
{
   esxcfg-init --alert "${*}"
   echo "${*}" >&2
}

mark_is_shutdown()
{
   case "${1}" in
      "0")
         eval "is_shutdown() { return 1 ; }"
      ;;
      "1")
         eval "is_shutdown() { return 0 ; }"
      ;;
      *)
         echo "Invalid parameter for is_shutdown: ${1}" >&2
         return 1
      ;;
   esac

   return 0
}

verify_ssl_certificates()
{
   [ -s "/etc/vmware/ssl/rui.key" ] && [ -s "/etc/vmware/ssl/rui.crt" ]
}

update_bootcfg()
{
   local bootbank=${1}

   if [ -s "${bootbank}/state.tgz" ] ; then
      if ! grep -q -e '--- state.tgz' "${bootbank}/boot.cfg" ; then
         sed -e '/^modules=/{ s/$/ --- state.tgz/ }' "${bootbank}/boot.cfg" > "${bootbank}/boot.cfg.$$"
         [ -s "${bootbank}/boot.cfg.$$" ] && mv -f "${bootbank}/boot.cfg.$$" "${bootbank}/boot.cfg"
         rm -f "${bootbank}/boot.cfg.$$"
         sync
      fi
   fi
}

update_useroptsgz()
{
   local bootbank=${1}

   gunzip -c "${bootbank}/useropts.gz" > "/tmp/useropts_old.$$"
   esxcfg-info -c > "/tmp/useropts.$$"

   diff -q "/tmp/useropts.$$" "/tmp/useropts_old.$$" >/dev/null 2>&1 || {
      # save kernel options
      if gzip "/tmp/useropts.$$" ; then
         # move from /tmp to ${bootbank} without overwriting useropts.gz so that an
         # interrupted copy doesn't corrupt useropts.gz  If the move succeeds, we
         # will rename the temporary file to boot.cfg (this assumes that rename
         # is effectively atomic).
         if mv -f "/tmp/useropts.$$.gz" "${bootbank}/useropts.$$.gz" ; then
            mv -f "${bootbank}/useropts.$$.gz" "${bootbank}/useropts.gz"
         else
            sysalert "Failed to move useropts.gz from /tmp to ${bootbank}.  Updated kernel options may be lost"
         fi
      else
         sysalert "Failed to create useropts.gz in /tmp. Updated kernel options may be lost."
      fi
   }

   rm -f "/tmp/useropts_old.$$"
   rm -f "/tmp/useropts.$$"
   rm -f "/tmp/useropts.$$.gz"

   sync
}

FileSystemCheckRequired()
{
   local fsCheck=$(vsish -e get /vmkModules/vfat/fsInfo | awk -F: '/fsCheck/ {print $2}')

   if [ $(bootOption -rf) -eq 0 -a "$fsCheck" = "0" ] ; then
      return ${FALSE}
   else
      return ${TRUE}
   fi
}

GetPrimaryBootVolume()
{
   local BootUUID=$(esxcfg-info -b 2> /dev/null)
   local BootVolume=

   if [ -n "${BootUUID}" ] ; then
      BootVolume="/vmfs/volumes/${BootUUID}"
   fi

   echo ${BootVolume}
}

GetHBAFromVolume()
{
   echo $(vmkfstools -P "$1" 2> /dev/null | awk '/^Partitions/ { getline; print gensub(/.*[\t ]([^ ]+):[0-9]+.*/, "\\1", "", $0); }')
}

GetBootHBA()
{
   local BootVolume=$(GetPrimaryBootVolume)
   local BootHBA=

   if [ -n "${BootVolume}" ] ; then
      BootHBA=$(GetHBAFromVolume "${BootVolume}")
   fi

   echo ${BootHBA}
}

RunFileSystemCheck()
{
   local BootDevice=$(GetBootHBA)

   for partition in 5 6 8 ; do
      disk="/dev/disks/${BootDevice}:${partition}"

      if [ -f "${disk}" ] ; then
         dosfsck -a -v "${disk}" || sysalert "Possible corruption on ${disk}"
      fi
   done
}

#
# if grep -q '^bootstate=1' /altbootbank/boot.cfg ; then
#   if [ -f /var/run/update_altbootbank ] ; then
#      ### write config to /altbootbank/state.tgz
#   else
#      ### write config to /bootbank/state.tgz
#      ### cp /bootbank/state.tgz /altbootbank/state.tgz
#   fi
# else
#    ### write config to /bootbank/state.tgz
# fi
#

main()
{
   local bootbank=${2}
   local lock=
   local update_alt_bootbank=""

   # check parameters
   if [ ${#} -lt 1 ] ; then
      echo "Usage: ${0} IsShutdown [PATH_NAME]" >&2
      return ${EXIT_SUCCESS}
   fi

   if [ -z "${bootbank}" -a -f "${LIVEINST_MARKER}" -a -f /altbootbank/boot.cfg ] ; then
      update_alt_bootbank=$(awk -F= '/^bootstate=[0-9]/{ print $2 }' /altbootbank/boot.cfg)
   fi

   if [ -z "${bootbank}" ] ; then
      if  [ "${update_alt_bootbank}" = "0" ] ; then
         # When LiveVib is installed, altbootbank_bootstate is set to 0.
         bootbank='/altbootbank'
      else
         bootbank='/bootbank'
      fi
   fi

   lock="/tmp/$(basename "${bootbank}").lck"

   mark_is_shutdown "${1}" || return ${EXIT_FAILURE}

   # audit-mode check
   [ "$(bootOption -ri)" = "1" ] && return ${EXIT_SUCCESS}

   # XXX Sanity check for QA.  See Bug #184932 for more information.
   # Panic and halt shutdown if the SSL certificates are invalid
   if ! verify_ssl_certificates ; then
      sysalert "SSL certificates are invalid"
      is_shutdown || return ${EXIT_FAILURE}
      while true ; do : ; done
   fi

   if [ ! -d "${bootbank}" ] ; then
      sysalert "Bootbank cannot be found at path '${bootbank}'"
      return ${EXIT_FAILURE}
   fi

   # Obtain a backup lock to prevent simultaneous backups with the same target from
   # clobbering one another.  Get the esx.conf lock at the same time to be sure we
   # get a consistent view of the configuration.
   #
   # When called from shutdown, we will break locks so that a dead lock holder
   # doesn't prevent us from completing.  Otherwise we will exit without doing
   # anything if we timeout on the locks
   if [ -f "${lock}" ] ; then
      local pid=$(cat "${lock}")

      if [ -n "${pid}" ] ; then
         kill -0 "${pid}" >/dev/null 2>&1 || rm -f "${lock}"
      else
         rm -f "${lock}"
      fi
   fi

   if is_shutdown ; then
      # timeout is 1 min
      lockfile -l 60 "${lock}"
      esxcfg-init -L $$
   else
      lockfile -3 -r 20 "${lock}" || return ${EXIT_FAILURE}
      esxcfg-init -L $$ || {
         rm -f "${lock}"
         return ${EXIT_FAILURE}
      }
   fi

   # backup counter with creation and modification time
   COUNTER_FILE="/etc/vmware/.backup.counter"

   if [ -f $COUNTER_FILE ]
   then
      COUNTER=$(cat $COUNTER_FILE | grep -v '#')
      STR_CREATED=$(cat $COUNTER_FILE | grep '# CREATED:')
   fi
   if [ -z "$COUNTER" ]
   then
      COUNTER=0
   fi
   if [ -z "$STR_CREATED" ]
   then
      STR_CREATED="# CREATED: $(date)"
   fi
   NEW_COUNTER=$(expr $COUNTER + 1)

   # update counter file
   echo "# This file is owned and updated by /sbin/backup.sh" >$COUNTER_FILE
   echo $STR_CREATED >>$COUNTER_FILE
   echo "# MODIFIED: $(date)" >>$COUNTER_FILE
   echo $NEW_COUNTER >>$COUNTER_FILE

   [ -z "$VMSUPPORT_MODE" ] && echo "Saving current state in ${bootbank}"
   (
      cd /

      # Save all modified files in /etc.
      # Omit files a) where the .# file exists but the original one doesn't.
      #            b) specified to be skipped.
      : "${files_to_skip:=}"
      local files_to_save=$(find etc -follow -type f -name '.#*' 2> /dev/null | \
                            sed -e 's,.#\(.*\),\1,g' |                          \
                            while read name ; do  \
                               if [ -f "${name}" ]; then echo ${files_to_skip} | \
                               grep -q ${name} || echo "${name}"; fi; \
                            done)

      # If running for vm-support, just print the file list.
      if [ -n "$VMSUPPORT_MODE" ] && [ -n "${files_to_save}" ]; then
         echo $files_to_save >&1
         esxcfg-init -U $$
      fi 

      # Otherwise, create state.tgz.
      if [ -z "$VMSUPPORT_MODE" ] && [ -n "${files_to_save}" ]; then
         
         # cleanup possible file leakage
         rm -rf "${bootbank}"/local.tgz.*
         rm -rf "${bootbank}"/state.tgz.*

         # Write to a temp file on same filesystem and then rename the file so
         # that we don't get a corrupted local.tgz if we are killed while
         # running tar.  Try twice at shutdown.
         #
         # Verify the files between operations as power failures and flash media
         # caching are known to make state saving an unreliable process if done
         # naively.  See Bug #332281 and Bug #363887 for more information.
         for try in 0 1 ; do
            local res=0

            tar czf "${bootbank}/local.tgz.$$" -C / ${files_to_save}
            res=$?

            if ! is_shutdown ; then
               esxcfg-init -U $$
            fi

            if [ ${res} -eq 0 -a -s "${bootbank}/local.tgz.$$" ] ; then
               mkdir -p "${bootbank}/state.$$"

               mv "${bootbank}/local.tgz.$$" "${bootbank}/state.$$/local.tgz"

               if tar czf "${bootbank}/state.tgz.$$" -C "${bootbank}/state.$$" local.tgz ; then
                  if [ -s "${bootbank}/state.tgz.$$" ] ; then
                     mv -f "${bootbank}/state.tgz.$$" "${bootbank}/state.tgz"
                  fi
               else
                  sysalert "failed to create state.tgz"
               fi

               sync

               rm -rf "${bootbank}/state.$$"
            else
               if ! is_shutdown || [ ${try} -eq 1 ] ; then
                  sysalert "Error (${res}) saving state to ${bootbank}"
                  res=1
                  break
               fi
            fi

            if ! is_shutdown || [ ${res} -eq 0 ] ; then
               break
            fi
         done
      fi

      if [ -z "${files_to_save}" ] || is_shutdown ; then
         esxcfg-init -U $$
      fi
   )

   # sanity check altbootbank if we have just upgraded
   if is_shutdown && [ -f /altbootbank/boot.cfg ] ; then
      local bootbank_serial=$(awk -F= '/^updated/{ print $2 }' /bootbank/boot.cfg)
      local altbootbank_serial=$(awk -F= '/^updated/{ print $2 }' /altbootbank/boot.cfg)
      local altbootbank_state=$(awk -F= '/^bootstate/{ print $2 }' /altbootbank/boot.cfg)
      local failures=0

      if [ ${bootbank_serial} -lt ${altbootbank_serial} -a ${altbootbank_state} -lt 2 ] ; then
         # refresh state.tgz in altbootbank when the host is updated.
         # Normal vib update: altbootbank_state = 1
         # Live vib update: altbootbank_state = 0
         if [ -d /bootbank -a -d /altbootbank -a "${bootbank}" != '/altbootbank' ] ; then
            cp -f /bootbank/state.tgz /altbootbank/state.tgz.$$ && \
               mv -f /altbootbank/state.tgz.$$ /altbootbank/state.tgz
            sync
         fi

         for file in /altbootbank/* ; do
            [ -f "${file}" ] || continue

            VerifyCopiedArchive "${file}" || {
               res=$?

               sysalert "New version of ${file} appears corrupt, upgrade may fail"
               failures=$(( ${failures} + 1 ))
            }
         done

         if [ ${failures} -gt 0 ] ; then
            sysalert "New upgrade image appears corrupted, upgrade may fail"
            sleep 10
         fi
      fi
   fi

   # Sync hardware clock
   hwclock $(date -u "+-t %H:%M:%S -d %m/%d/%Y") >&2

   # Save vmkernel options
   # Do this after unlocking esx.conf.LOCK.
   # Potentially we could have a mismatch between esx.conf and the saved
   # options. We will ignore the last minute change and address it in the next
   # backup cycle.
   if [ -e "${bootbank}/boot.cfg" ]; then
      update_bootcfg "${bootbank}" || {
         res=$?
         sysalert "Failed to update boot.cfg on ${bootbank}"
      }
   fi

   if [ -e "${bootbank}/useropts.gz" ]; then
      update_useroptsgz "${bootbank}"
   fi


   # In the case of shutdown don't delete the lock.
   # lockfile is in ramdisk so shutdown should take care of deleting it.
   if ! is_shutdown ; then
      rm -f "${lock}"
   else
      # run file system check if necessary
      if FileSystemCheckRequired ; then
         echo "Starting filesystem check on VFAT partitions" >&2
         RunFileSystemCheck
      fi
   fi

   return ${res}
}

main "${@}"

