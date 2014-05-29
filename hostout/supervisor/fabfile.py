import os
import os.path  #import os.path.join, os.path.basename, os.path.dirname
from fabric import api, contrib
from collective.hostout.hostout import buildoutuser, asbuildoutuser
#from collective.hostout.hostout import  assudouser
import time


def supervisorboot():
    """Ensure that supervisor is started on boot"""
    hostout = api.env.hostout

    sudosupervisor = hostout.options.get("sudosupervisor", '')
    supervisor = sudosupervisor or hostout.options.get("supervisor")

    if supervisor is None:
        raise Exception ("No supervisor listed")

    if sudosupervisor == '':  
        effective_user = hostout.options.get("effective-user")
        cmdbase = "sudo -u \"%s\" bin/" % effective_user
    else:
        cmdbase = "bin/"

    cmdbase += supervisor
    name = "%s-%s" % (hostout.name, supervisor)

    hostout.install_bootscript (cmdbase + "d", cmdbase + "ctl shutdown", name)     


def predeploy():
    api.env.superfun()
    hostout = api.env.hostout
    rollingrestart = hostout.options.get("rollingrestart", False)
    if not rollingrestart:
        api.env.hostout.supervisorshutdown()
    if hostout.options.get('install-on-startup') is not None:
        api.env.hostout.installonstartup()

def postdeploy():
    api.env.superfun()
    hostout = api.env.hostout
    rollingrestart = hostout.options.get("rollingrestart", False)
    if rollingrestart:
        api.env.hostout.supervisorshutdown()
        api.env.hostout.supervisorstartup()
    else:
        api.env.hostout.supervisorstartup()

def supervisorstartup():
    """Start the supervisor daemon"""
    hostout = api.env.hostout
    path = hostout.getRemoteBuildoutPath()
    bin = "%(path)s/bin" % locals()
    supervisor = hostout.options.get('sudosupervisor') or hostout.options.get('supervisor')
    try:
        with asbuildoutuser():
            api.run("%(bin)s/%(supervisor)sctl reload"% dict(bin=bin, supervisor=supervisor))
    except:
        if hostout.options.get('sudosupervisor','').strip():
            with api.settings(warn_only=True):
                api.sudo("%(bin)s/%(supervisor)sctl shutdown"% dict(bin=bin, supervisor=supervisor))
            api.sudo("%(bin)s/%(supervisor)sd"% dict(bin=bin, supervisor=supervisor))
        else:

            buildout_user = hostout.options.get("buildout-user")
            effective_user = hostout.options.get("effective-user")
            if effective_user == buildout_user:
                with asbuildoutuser():
                    api.run("%(bin)s/%(supervisor)sd"% dict(bin=bin, supervisor=supervisor))
            else:
#                with assudouser():
                    api.sudo ("%(bin)s/%(supervisor)sd" % dict(bin=bin, supervisor=supervisor), user=effective_user)

        time.sleep(5) # give it a little chance
    
    api.env.hostout.supervisorctl('status')


@buildoutuser
def supervisorshutdown():
    """Shutdown the supervisor daemon"""
    api.env.hostout.supervisorctl('stop all',ignore_errors=True)
    
@buildoutuser
def supervisorctl(*args, **vargs):
    """Runs remote supervisorlctl with given args"""
    hostout = api.env.hostout
    path = hostout.getRemoteBuildoutPath()
    bin = "%(path)s/bin" % locals()
    supervisor = hostout.options.get('sudosupervisor') or hostout.options.get('supervisor')
    if not args:
        args = ['status']
    args = ' '.join(args)
    try:
        api.run("%(bin)s/%(supervisor)sctl %(args)s" % locals())
    except:
        if vargs.get('ignore_errors'):
            return False
        else:
            raise
    return True


@buildoutuser
def restart(*args):
    """ supervisorctl restart command """
    api.env.hostout.supervisorctl('restart', *args)

@buildoutuser
def start(*args):
    """ supervisorctl start command """
    api.env.hostout.supervisorctl('start', *args)
@buildoutuser
def stop(*args):
    """ supervisorctl stop command """
    api.env.hostout.supervisorctl('stop', *args)
@buildoutuser
def status(*args):
    """ supervisorctl status command """
    api.env.hostout.supervisorctl('status', *args)
@buildoutuser
def tail(*args):
    """ supervisorctl tail command """
    api.env.hostout.supervisorctl('tail', *args)
