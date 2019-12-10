#! /usr/bin/python3

import sys

from gi.repository import GLib, Gio
from desktopconfig import DesktopConfig

session_bus = Gio.BusType.SESSION
cancellable = None
connection = Gio.bus_get_sync(session_bus, cancellable)

proxy_property = 0
interface_properties_array = None
destination = 'org.xfce.Xfconf'
path = '/org/xfce/Xfconf'
interface = destination

xfconf = Gio.DBusProxy.new_sync(
    connection,
    proxy_property,
    interface_properties_array,
    destination,
    path,
    interface,
    cancellable)

if len(sys.argv) > 1:
    if sys.argv[1] in ['save', 'load']:
        try:
            if sys.argv[1] == 'save':
                DesktopConfig.from_xfconf(xfconf).to_file(sys.argv[2])
            elif sys.argv[1] == 'load':
                DesktopConfig.from_file(sys.argv[2]).to_xfconf(xfconf)
        except Exception as e:
            print(repr(e))
            exit(1)
        exit(0)

