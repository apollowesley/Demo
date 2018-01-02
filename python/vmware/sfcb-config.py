#!/usr/bin/python

__doc__ = """
@file sfcb-config.py --
Copyright 2010 VMware, Inc.  All rights reserved.
-- VMware Confidential

This module upgrades /etc/sfcb/sfcb.cfg .
"""

__author__ = "VMware, Inc"

import os
import sys
import optparse
import shutil

VMWARE_BIN = "/bin/vmware"

CONFIG_BASE_NAME = "sfcb.cfg"
ROOT_CFG = "etc/sfcb"
SFCB_CFG_PATH = "%s/%s" % (ROOT_CFG, CONFIG_BASE_NAME)

def getVMwareVersion():
  import subprocess as sub
  p = sub.Popen('%s -v' % VMWARE_BIN, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
  output, errors = p.communicate()
  return output.strip()

VMWARE_V = getVMwareVersion()

def log(msg):
   sys.stdout.write("%s\n" % (msg.strip()))

def processArgs():
   parser = optparse.OptionParser()
   parser.add_option('--config-stage', dest='stageroot', metavar='PATH',
         help='Path to root of staged configuration files.')
   options, args = parser.parse_args()

   if options.stageroot is None:
      parser.error('Missing --config-stage option')

   return options


def getProperties(fn):
   properties = {}
   for line in file(fn):
       # ignore comments
       if line.startswith("#"):
          continue
       (n, c, v) = line.strip().partition(':')
       if v:
          properties[n.strip()] = v
   return properties


def setPermissions(target, removesticky=False):
   # can't use stat values as they don't have a macro
   # for setting the sticky bit
   # 0x3A4 (hex) -> 1644 (octal)
   # 0x124 (hex) -> 444 (octal)
   if removesticky:
      os.chmod(target, 0x124)
   else:
      os.chmod(target, 0x3A4)

sfcbobsoletes = ['logLevel']
sfcbupdates = ['basicAuthLib',
               'providerDirs',
               'registrationDir',
               'certificateAuthLib',
               'sslClientCertificate',
               'sslClientTrustStore',
               'sslCertificateFilePath',
               'sslKeyFilePath',]


def migrateLogLevel(level):
   '''
   Migrate logLevel to esxcfg advance configuration.
   '''
   if level in [str(l) for l in range(8)]:
      try:
         os.system("/sbin/esxcfg-advcfg -q -s %s /UserVars/CIMLogLevel" % (level))
      except Exception, e:
         log("--- sfcb  error in migrating CIMLogLevel: %s", e)
   else:
      log("--- sfcb ignore unrecognized sfcb logLevel : %s" % (level))


def migrateSfcbConfig(options):
   '''
   Migrate an SFCB Config to the current format. Config properties in obsoletes list will be
   dropped in new config file. Config properties in updates list will be updated with the
   value in updated config file. Other customer config properties will be kept unchanged.
   New config properties in update config file will be added.
   '''
   # c: customer u: update n: new
   cfile = os.path.join(options.stageroot, SFCB_CFG_PATH)
   ufile = os.path.join(options.stageroot, "%s.new" % SFCB_CFG_PATH)

   if not os.path.isfile(ufile):
      log("-- %s.new doesn't exist --" % CONFIG_BASE_NAME)
      return False

   if not os.path.isfile(cfile):
      log("-- %s doesn't exist so using current version --" % CONFIG_BASE_NAME)
      shutil.copy(ufile, cfile)
      setPermissions(cfile)
      return True

   # ensure permissions are correct
   setPermissions(cfile)

   cps = getProperties(cfile)
   ups = getProperties(ufile)
   nps = {}

   # respect various migration settings
   for p in cps:
      if p not in sfcbobsoletes:
         nps[p] = cps[p]

      if p == 'logLevel':
         migrateLogLevel(cps[p].strip())

   for p in ups:
      if p not in cps or p in sfcbupdates:
         nps[p] = ups[p]

   if os.path.isfile(cfile):
      # make a backup of the old config just in case we screw something up
      shutil.move(cfile, cfile + '.old')
      setPermissions(cfile + '.old', removesticky=True)

   f = open(cfile, 'w')
   f.write('# Generated by sfcb-config.py. Do not modify this header.\n')
   f.write('# %s\n' % VMWARE_V)
   f.write('#\n')
   for p in sorted(nps.keys()):
      f.write('%s:%s\n' % (p, nps[p]))
   f.close()
   setPermissions(cfile)
   return True

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def main():
   options = processArgs()
   if migrateSfcbConfig(options):
      log("-- sfcb configuration update is done --")
      return EXIT_SUCCESS
   else:
      log("-- an error occurred --")
      return EXIT_FAILURE

if __name__ == '__main__':
   sys.exit(main())