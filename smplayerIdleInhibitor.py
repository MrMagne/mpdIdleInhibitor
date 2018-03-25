#!/usr/bin/python

import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
from functools import partial, reduce
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='verbose', action='store_true')
args = parser.parse_args()
verboseprint = print if args.verbose else lambda *a, **k: None

DBusGMainLoop(set_as_default=True)
loop = GObject.MainLoop()

session_bus = dbus.SessionBus()
sessionManager = session_bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
register = sessionManager.get_dbus_method('RegisterClient', 'org.gnome.SessionManager')
unregister = sessionManager.get_dbus_method('UnregisterClient', 'org.gnome.SessionManager')
inhibit = sessionManager.get_dbus_method('Inhibit', 'org.gnome.SessionManager')
uninhibit = sessionManager.get_dbus_method('Uninhibit', 'org.gnome.SessionManager')
cookie = None
states = {}
watches = {}
def UninhibitIfNeeded():
    global cookie
    global states
    if ((not cookie is None) and not(reduce(lambda acc, val: acc or val, states.values(), False))):
        verboseprint('uninhibiting')
        uninhibit(cookie)
        cookie = None


def NameOwnerCb(watched_name, name):
    global states
    global watches
    if (name == ""):
        verboseprint('%s is gone'%watched_name)
        states[watched_name] = False
        UninhibitIfNeeded()
        if (watched_name in watches):
            del watches[watched_name]

def PlaybackStatusCb(*args, **kwargs):
    global cookie
    global states
    sender=kwargs['sender']
    if (len(args)>1 and 'PlaybackStatus' in args[1]):
        if(args[1]['PlaybackStatus'] == 'Playing'):
            if (not sender in watches):
                watches[sender] = session_bus.watch_name_owner(sender, partial(NameOwnerCb, sender))
            states[sender] = True
            verboseprint('inhib %s'%sender)
            if (cookie is None):
                verboseprint('inhibiting')
                cookie=inhibit(appId, 0, 'smplayer is playing', 8); #8 =>flag for idle
        else:
            verboseprint('uninhib %s'%sender)
            states[sender] = False
            UninhibitIfNeeded()

appId = register('smplayerIdleInhibitor', 'smplayerIdleInhibitor.0')

try:
    session_bus.add_signal_receiver(PlaybackStatusCb,
            dbus_interface='org.freedesktop.DBus.Properties',
            signal_name='PropertiesChanged',
            #bus_name='org.mpris.MediaPlayer2.smplayer',
            sender_keyword='sender',
            path='/org/mpris/MediaPlayer2')
    loop.run()
except:
    print('smplayerIdleInhibitor shutting down')
finally:
    if (not cookie is None):
        uninhibit(cookie)
    unregister(appId)
