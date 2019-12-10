#!/usr/bin/env python3
# *
# * Source based on Configuration switcher for xfce4-panel
# *
# * Copyright 2013 Alistair Buxton <a.j.buxton@gmail.com>
# * Copyright 2019 Daniel Ruiz de Alegría <daniel@drasite.com>
# *
# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.

from gi.repository import Gio, GLib
import tarfile
import io
import time
import os
import re

# yes, python 3.2 has exist_ok, but it will still fail if the mode is different


def mkdir_p(path):
    try:
        os.makedirs(path, exist_ok=True)
    except FileExistsError:
        pass


def add_to_tar(t, bytes, arcname):
    ti = tarfile.TarInfo(name=arcname)
    ti.size = len(bytes)
    ti.mtime = time.time()
    f = io.BytesIO(bytes)
    t.addfile(ti, fileobj=f)


class DesktopConfig(object):

    def __init__(self):
        self.desktops = []
        self.panel_properties = {}
        self.desktop_properties = {}
        self.notifyd_properties = {}
        self.source = None

    @classmethod
    def from_xfconf(cls, xfconf):
        dc = DesktopConfig()

        dc.panel_properties = dc.read_xfconf_properties(xfconf, 'xfce4-panel')
        dc.desktop_properties = dc.read_xfconf_properties(xfconf, 'xfce4-desktop')
        dc.notifyd_properties = dc.read_xfconf_properties(xfconf, 'xfce4-notifyd')

        dc.remove_panel_orphans()
        dc.find_desktops()

        dc.source = None

        return dc

    @classmethod
    def from_file(cls, filename):
        dc = DesktopConfig()

        dc.source = tarfile.open(filename, mode='r')

        dc.panel_properties = dc.read_file_properties('panel.txt')
        dc.desktop_properties = dc.read_file_properties('desktop.txt')
        dc.notifyd_properties = dc.read_file_properties('notifyd.txt')

        dc.remove_panel_orphans()
        dc.find_desktops()

        return dc

    def read_xfconf_properties(self, xfconf, channel):
        result = xfconf.call_sync(
            'GetAllProperties',
            GLib.Variant('(ss)', (channel, '')), 0, -1, None)

        props = result.get_child_value(0)
        properties = {}

        for n in range(props.n_children()):
            p = props.get_child_value(n)
            pp = p.get_child_value(0).get_string()
            pv = p.get_child_value(1).get_variant()

            pn = GLib.Variant.parse(None, str(pv), None, None)
            assert(pv == pn)

            properties[pp] = pv

        return properties

    def read_file_properties(self, filename):
        config = self.source.extractfile(filename)

        properties = {}

        for line in config:
            try:
                x = line.decode('utf-8').strip().split(' ', 1)
                properties[x[0]] = GLib.Variant.parse(None, x[1], None, None)
            except:
                pass

        return properties

    def remove_panel_orphans(self):
        plugin_ids = set()
        rem_keys = []

        for pp, pv in self.panel_properties.items():
            path = pp.split('/')
            if len(path) == 4 and path[0] == '' and path[1] == 'panels' and \
                    path[2].startswith('panel-') and path[3] == 'plugin-ids':
                plugin_ids.update(pv)

        for pp, pv in self.panel_properties.items():
            path = pp.split('/')
            if len(path) == 3 and path[0] == '' and path[1] == 'plugins' and \
                    path[2].startswith('plugin-'):
                number = path[2].split('-')[1]
                try:
                    if int(number) not in plugin_ids:
                        rem_keys.append('/plugins/plugin-' + number)
                except ValueError:
                    pass

        self.remove_keys(rem_keys)

    def check_desktop(self, path):
        try:
            bytes = self.get_desktop_source_file(path).read()
        except FileNotFoundError:
            # If the .desktop file does not exist at all return False
            return False

        # Check if binary exists
        keyfile = GLib.KeyFile.new()
        decoded = bytes.decode()
        if keyfile.load_from_data(decoded, len(decoded),
                                  GLib.KeyFileFlags.NONE):
            try:
                exec_str = keyfile.get_string("Desktop Entry", "Exec")
                if self.check_exec(exec_str):
                    return True
            except GLib.Error:  # pylint: disable=E0712
                pass #  https://bugzilla.xfce.org/show_bug.cgi?id=14597

        return False

    def find_desktops(self):
        rem_keys = []

        for pp, pv in self.panel_properties.items():
            path = pp.split('/')
            if len(path) == 3 and path[0] == '' and path[1] == 'plugins' and \
                    path[2].startswith('plugin-'):
                number = path[2].split('-')[1]
                if pv.get_type_string() == 's' and \
                        pv.get_string() == 'launcher':
                    for d in self.panel_properties['/plugins/plugin-' + number +
                                             '/items'].unpack():
                        desktop_path = 'launcher-' + number + '/' + d
                        if self.check_desktop(desktop_path):
                            self.desktops.append(desktop_path)
                        else:
                            rem_keys.append('/plugins/plugin-' + number)

        self.remove_keys(rem_keys)

    def remove_keys(self, rem_keys):
        keys = list(self.panel_properties.keys())
        for param in keys:
            for bad_plugin in rem_keys:
                if param == bad_plugin or param.startswith(bad_plugin+'/'):
                    try:
                        del self.panel_properties[param]
                    except KeyError:
                        pass #  https://bugzilla.xfce.org/show_bug.cgi?id=14934

    def get_desktop_source_file(self, desktop):
        if getattr(self, 'source', None) is None:
            path = os.path.join(
                GLib.get_home_dir(), '.config/xfce4/panel/', desktop)
            return open(path, 'rb')
        else:
            return self.source.extractfile(desktop)

    def to_file(self, filename):
        if filename.endswith('.gz'):
            mode = 'w:gz'
        elif filename.endswith('.bz2'):
            mode = 'w:bz2'
        else:
            mode = 'w'
        t = tarfile.open(name=filename, mode=mode)
        panel_properties_text = self.get_properties_text(self.panel_properties)
        desktop_properties_text = self.get_properties_text(self.desktop_properties)
        notifyd_properties_text = self.get_properties_text(self.notifyd_properties)
        add_to_tar(t, '\n'.join(panel_properties_text).encode('utf8'), 'panel.txt')
        add_to_tar(t, '\n'.join(desktop_properties_text).encode('utf8'), 'desktop.txt')
        add_to_tar(t, '\n'.join(notifyd_properties_text).encode('utf8'), 'notifyd.txt')

        for d in self.desktops:
            bytes = self.get_desktop_source_file(d).read()
            add_to_tar(t, bytes, d)

        t.close()

    def get_properties_text(self, properties):
        props_tmp = []
        for (pp, pv) in sorted(properties.items()):
            props_tmp.append(str(pp) + ' ' + str(pv))
        return props_tmp

    def check_exec(self, program):
        program = program.strip()
        if len(program) == 0:
            return False

        params = list(GLib.shell_parse_argv(program)[1])
        executable = params[0]

        if os.path.exists(executable):
            return True

        path = GLib.find_program_in_path(executable)
        if path is not None:
            return True

        return False

    def to_xfconf(self, xfconf):
        session_bus = Gio.BusType.SESSION
        conn = Gio.bus_get_sync(session_bus, None)

        destination = 'org.xfce.Panel'
        path = '/org/xfce/Panel'
        interface = destination

        dbus_proxy = Gio.DBusProxy.new_sync(conn, 0, None, destination, path, interface, None)

        if dbus_proxy is not None:
            self.set_properties(xfconf, 'xfce4-panel', self.panel_properties)

            panel_path = os.path.join(
                GLib.get_home_dir(), '.config/xfce4/panel/')
            for d in self.desktops:
                bytes = self.get_desktop_source_file(d).read()
                mkdir_p(panel_path + os.path.dirname(d))
                f = open(panel_path + d, 'wb')
                f.write(bytes)
                f.close()

            try:
                dbus_proxy.call_sync('Terminate', GLib.Variant('(b)', ('xfce4-panel',)), 0, -1, None)
            except GLib.GError:  # pylint: disable=E0712
                pass

        self.configure_desktop_monitors(xfconf)
        self.set_properties(xfconf, 'xfce4-desktop', self.desktop_properties)

        self.set_properties(xfconf, 'xfce4-notifyd', self.notifyd_properties)

    def configure_desktop_monitors(self, xfconf):
        fallback_monitor = '/backdrop/screen0/monitor0/'
        fallback_monitor_properties = {}
        prev_desktop_properties = self.read_xfconf_properties(xfconf, 'xfce4-desktop')

        for pp in self.desktop_properties:
            if re.match('^' + fallback_monitor + '[^/\s]+$', pp):
                fallback_monitor_properties[pp.replace(fallback_monitor, '')] = \
                        self.desktop_properties[pp]

        for pp in prev_desktop_properties:
            w = re.search('^/backdrop/screen\d/monitor[^/]+/workspace\d/', pp)
            if w:
                for fpp in fallback_monitor_properties:
                    new_pp = w.group(0) + fpp
                    if new_pp not in self.desktop_properties:
                        self.desktop_properties[new_pp] = \
                                fallback_monitor_properties[fpp]

    def set_properties(self, xfconf, channel, properties):
        # Reset all properties to make sure old settings are invalidated
        try:
            xfconf.call_sync('ResetProperty', GLib.Variant(
                '(ssb)', (channel, '/', True)), 0, -1, None)
        except GLib.Error:  # pylint: disable=E0712
            pass

        for (pp, pv) in sorted(properties.items()):
            xfconf.call_sync('SetProperty', GLib.Variant(
                '(ssv)', (channel, pp, pv)), 0, -1, None)
