#!/usr/bin/python

import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
loop = GObject.MainLoop()

session_bus = dbus.SessionBus()
sessionManager = session_bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
register = sessionManager.get_dbus_method('RegisterClient', 'org.gnome.SessionManager')
unregister = sessionManager.get_dbus_method('UnregisterClient', 'org.gnome.SessionManager')
inhibit = sessionManager.get_dbus_method('Inhibit', 'org.gnome.SessionManager')
uninhibit = sessionManager.get_dbus_method('Uninhibit', 'org.gnome.SessionManager')
cookie = None

def PlaybackStatusCb(*args, **kwargs):
    global cookie
    if (len(args)>1 and 'PlaybackStatus' in args[1]):
        if(args[1]['PlaybackStatus'] == 'Playing'):
            if (cookie is None):
                cookie=inhibit(appId, 0, 'smplayer is playing', 8); #8 =>flag for idle
        else:
            if (not cookie is None):
                uninhibit(cookie)
                cookie = None

appId = register('smplayerIdleInhibitor', 'smplayerIdleInhibitor.0')

try:
    session_bus.add_signal_receiver(PlaybackStatusCb,
            dbus_interface='org.freedesktop.DBus.Properties',
            signal_name='PropertiesChanged',
            bus_name='org.mpris.MediaPlayer2.smplayer',
            path='/org/mpris/MediaPlayer2')
    loop.run()
except:
    print('smplayerIdleInhibitor shutting down')
finally:
    if (not cookie is None):
        uninhibit(cookie)
    unregister(appId)
