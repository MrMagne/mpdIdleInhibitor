#!/usr/bin/python

import dbus
from mpd import MPDClient

session_bus = dbus.SessionBus()
sessionManager = session_bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
register = sessionManager.get_dbus_method('RegisterClient', 'org.gnome.SessionManager')
unregister = sessionManager.get_dbus_method('UnregisterClient', 'org.gnome.SessionManager')
inhibit = sessionManager.get_dbus_method('Inhibit', 'org.gnome.SessionManager')
uninhibit = sessionManager.get_dbus_method('Uninhibit', 'org.gnome.SessionManager')

cookie = None
appId = register('mpdIdleInhibitor', 'mpdIdleInhibitor.0')

mpd = MPDClient()               # create client object
mpd.connect("localhost", 6600)  # connect to localhost:6600
try:
    while True:
        if (mpd.idle('player')):
            status = mpd.status()['state']
            if (status == 'play'):
                if (cookie is None):
                    cookie=inhibit(appId, 0, 'mpd is playing', 8); #8 =>flag for idle
                #print('playing')
            else:
                if (not cookie is None):
                    uninhibit(cookie)
                    cookie=None
                #print('not playing: '+status)
except:
    print('mpdIdleInhibitor shutting down')
finally:
    if (not cookie is None):
        uninhibit(cookie)
    unregister(appId)
    mpd.close()                     # send the close command
    mpd.disconnect()    
