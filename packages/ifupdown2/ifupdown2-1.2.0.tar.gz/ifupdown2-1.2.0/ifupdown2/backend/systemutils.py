#!/usr/bin/python
#
# Copyright 2015-2017 Cumulus Networks, Inc. All rights reserved.
# Author: Roopa Prabhu, roopa@cumulusnetworks.com
#

try:
    import os

    from ifupdown2.backend.utils import utils
    from ifupdown2.backend.utilsbase import *
except ImportError, e:
    raise ImportError('%s - required module not found' % str(e))

class systemUtils():
    @classmethod
    def is_service_running(cls, procname=None, pidfile=None):
        utilsobj = utilsBase()
        if pidfile:
            if os.path.exists(pidfile):
                pid = utilsobj.read_file_oneline(pidfile)
                if not os.path.exists('/proc/%s' %pid):
                    return False
            else:
                return False
            return True

        if procname:
            try:
                utils.exec_command('%s %s' %
                                    (utils.pidof_cmd, procname))
            except:
                return False
            else:
                return True

        return False

    @classmethod
    def check_service_status(cls, servicename=None):
        if not servicename:
            return False
        try:
            utils.exec_commandl([utils.service_cmd,
                                 servicename, 'status'])
        except Exception:
            # XXX: check for subprocess errors vs os error
            return False
        return True

    @classmethod
    def is_process_running(self, processname):
        if not processname:
            return False
        try:
            utils.exec_command('%s %s' %
                               (utils.pidof_cmd, processname))
        except:
            return False
        else:
            return True
