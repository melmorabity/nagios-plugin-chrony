#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2018 Mohamed El Morabity <melmorabity@fedoraproject.com>
#
# This module is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.


import re
import subprocess

from pynag import Plugins
from pynag.Plugins import simple as Plugin


DEFAULT_CHRONYD_PORT = 323

plugin = Plugin()

# Specify arguments to the plugin
plugin.add_arg('p', 'port', 'Chrony UDP port', required=None)

plugin.activate()

if plugin['critical'] <= plugin['warning']:
    plugin.parser.error('Critical level cannot be lesser than or equal to warning')

if plugin['host'] is None:
    plugin['host'] = 'localhost'

if plugin['port'] is None:
    plugin['port'] = DEFAULT_CHRONYD_PORT
else:
    try:
        plugin['port'] = float(plugin['port'])
        if plugin['port'] <= 0:
            raise ValueError
    except ValueError as ex:
        plugin.parser.error('Invalid port number')

# Run chrony tracking
command = ['chronyc', '-h', plugin['host'], '-p', str(plugin['port']), 'tracking']

try:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None)
    output = process.communicate()[0].decode('utf-8')
except OSError as ex:
    plugin.nagios_exit(Plugins.UNKNOWN, str(ex))

if process.returncode != 0:
    plugin.nagios_exit(Plugins.CRITICAL, output.rstrip())

matcher = re.search(r'^Leap status\s*:\s*(.*)$', output, flags=re.MULTILINE)
leap_status = matcher.group(1)
if leap_status == 'Not synchronised':
    plugin.nagios_exit(Plugins.CRITICAL, 'Server is not synchronised')
if leap_status == 'Unknown':
    plugin.nagios_exit(Plugins.UNKNOWN, 'Server status is unknown')

matcher = re.search(r'^System time\s*:\s*([0-9]+\.[0-9]*) seconds (slow|fast)', output,
                    flags=re.MULTILINE)
offset = float(matcher.group(1))

status = Plugins.check_threshold(abs(offset), warning=plugin['warning'],
                                 critical=plugin['critical'])
plugin.add_perfdata('offset', offset, uom='s', warn=plugin['warning'], crit=plugin['critical'])
plugin.nagios_exit(status, 'Offset {} seconds'.format(offset))
