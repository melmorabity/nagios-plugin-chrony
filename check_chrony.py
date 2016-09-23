#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2016 Mohamed El Morabity <melmorabity@fedoraproject.com>
#
# This module is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


import re
import subprocess
import pynag.Plugins


DEFAULT_CHRONYD_PORT = 323

helper = pynag.Plugins.PluginHelper()

# Specify arguments to the plugin
helper.parser.description = 'This plugin checks the clock offset of chronyd.'
helper.parser.add_option('-H', '--hostname', help='Host name or IP address')
helper.parser.add_option('-p', '--port', type='int', default=DEFAULT_CHRONYD_PORT, help='Chrony UDP port (default: %i)' % DEFAULT_CHRONYD_PORT)
helper.parser.add_option('-w', '--warning', type='float', help='Offset to result in warning status (in seconds)')
helper.parser.add_option('-c', '--critical', type='float', help='Offset to result in critical status (in seconds)')
helper.parse_arguments()

if not helper.options.hostname:
    helper.parser.error('Hostname is mandatory')
if not helper.options.warning:
    helper.parser.error('Warning level is mandatory')
if not helper.options.critical:
    helper.parser.error('Critical level is mandatory')
if helper.options.critical <= helper.options.warning:
    helper.parser.error('Critical level cannot be lesser than or equal to warning')

# Run chrony tracking
command = ['chronyc', '-h', helper.options.hostname, '-p', str(helper.options.port), 'tracking']
if helper.options.show_debug:
    command.append('-d')

try:
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
except OSError as e:
    helper.status(pynag.Plugins.unknown)
    helper.add_summary(str(e))
    helper.exit()

if p.returncode != 0:
    helper.status(pynag.Plugins.critical)
    helper.add_summary(output)
    helper.exit()
    
matcher = re.search("^Leap status\s*:\s*(.*)$", output, flags=re.MULTILINE)
leap_status = matcher.group(1)
if leap_status == 'Not synchronised':
    helper.status(pynag.Plugins.critical)
    helper.add_summary('Server is not synchronised')
    helper.exit()
if leap_status == 'Unknown':
    helper.status(pynag.Plugins.unknown)
    helper.add_summary('Server status is unknown')
    helper.exit()

matcher = re.search("^System time\s*:\s*([0-9]+\.[0-9]*) seconds (slow|fast)", output, flags=re.MULTILINE)
offset = float(matcher.group(1))
if matcher.group(2) == 'fast':
    offset = -offset
if abs(offset) >= helper.options.critical:
    helper.status(pynag.Plugins.critical)
elif abs(offset) >= helper.options.warning:
    helper.status(pynag.Plugins.warning)
else:
    helper.status(pynag.Plugins.ok)

helper.add_metric(label='offset', value='%.9f' % offset, uom='s')
helper.add_summary('Offset %g seconds' % offset)
helper.exit()
