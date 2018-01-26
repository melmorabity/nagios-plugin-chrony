# nagios-plugin-chrony

Nagios plugin to check the clock offset of chrony

## Authors

Mohamed El Morabity <melmorabity -(at)- fedoraproject.org>

## Usage

    check_chrony.py [--hostname HOSTNAME] --warning WARNING --critical CRITICAL [--port PORT]

### Options

    -h, --help

Show help message and exit

    -H HOSTNAME, --hostname=HOSTNAME

Host name or IP address

    -p PORT, --port=PORT

Chrony UDP port (default: 323)

    -w WARNING, --warning=WARNING

Offset to result in warning status (in seconds)

    -c CRITICAL, --critical=CRITICAL

Offset to result in critical status (in seconds)

## Examples

    $ ./check_chrony -H localhost -w 0.5 -c 1
    OK: Offset 0.000590362 seconds | 'offset'=0.000590362s;0.5;1;;
