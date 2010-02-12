import os
import os.path  #import os.path.join, os.path.basename, os.path.dirname
from fabric import api

initd = """
#!/bin/sh
#
# Supervisor init script.
#
# chkconfig: 2345 80 20
# description: supervisord

# Source function library.
. /etc/rc.d/init.d/functions

ENV=plonedev
BUILDOUT=%(bin)s
SUPERVISORD="%(supervisor)sd"
SUPERVISORCTL="%(supervisor)sctl"

RETVAL=0

start() {
     echo -n "Starting $SUPERVISORD: "
     $BUILDOUT/$SUPERVISORD
     RETVAL=$?
     [ $RETVAL -eq 0 ] && touch /var/lock/subsys/$SUPERVISORD-$ENV
     echo
     return $RETVAL
}

stop() {
     echo -n "Stopping $SUPERVISORD: "
     $BUILDOUT/$SUPERVISORCTL shutdown
     RETVAL=$?
     [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/$SUPERVISORD-$ENV
     echo
     return $RETVAL
}

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
esac

exit $REVAL
"""


def supervisorboot():
    """Ensure that supervisor is started on boot"""
    hostout = api.env.hostout

    # based on
    # http://www.webmeisterei.com/friessnegger/2008/06/03/control-production-buildouts-with-supervisor/
    bin = "%s/bin" % hostout.getRemoteBuildoutPath()
    supervisor = hostout.options['supervisor']
    #sudo('sh -c "cd /etc/init.d && ln -s %s/%sd %s-%sd"' % (bin, supervisor, hostout.name, supervisor))
    #sudo('sh -c "cd /etc/init.d && update-rc.d %s-%sd defaults"' % (hostout.name, supervisor))



def predeploy():
    hostout = api.env.hostout
    supervisorshutdown()
    if hostout.options.get('install-on-startup') is not None:
        installonstartup()

def postdeploy():
    supervisorstartup()
    
def supervisorstartup():
    """Start the supervisor daemon"""
    hostout = api.env.hostout
    bin = "%s/bin" % hostout.getRemoteBuildoutPath()
    supervisor = hostout.options['supervisor']
    api.sudo("%s/%sd"% (bin,supervisor))
    api.sudo("%s/%sctl status"% (bin,supervisor))

def supervisorshutdown():
    """Shutdown the supervisor daemon"""
    hostout = api.env.hostout
    bin = "%s/bin" % hostout.getRemoteBuildoutPath()
    supervisor = hostout.options['supervisor']
    api.run("%s/%sctl shutdown || echo 'Failed to shutdown'"% (bin,supervisor) )

def supervisorctl(*args):
    """Runs remote supervisorlctl with given args"""
    hostout = api.env.hostout
    bin = "%s/bin" % hostout.getRemoteBuildoutPath()
    supervisor = hostout.options['supervisor']
    if not args:
        args = ['status']
    api.run("%s/%sctl %s"% (bin,supervisor,' '.join(args)) )



