#    Copyright (C) 2010  Carlos Perez
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; Applies version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import ipaddress
import re
import socket

__name__ = 'whois.py'

WHOIS_PORT_NUMBER = 43
WHOIS_RECEIVE_BUFFER_SIZE = 4096


def get_whois(ip_addrs):
    """
    Function that returns what whois server is the one to be queried for
    registration information, returns whois.arin.net if not in database, returns
    None if private.
    """
    whois_server = None
    try:
        ip = ipaddress.ip_address(ip_addrs)
        if isinstance(ip, ipaddress.IPv4Address) and not ip.is_private:
            whois_server = 'whois.arin.net'
    except ValueError:
        whois_server = None

    return whois_server


def whois(target, whois_srv):
    """
    Performs a whois query against a arin.net for a given IP, Domain or Host as a
    string and returns the answer of the query.
    """
    response = ''
    counter = 1
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((whois_srv, WHOIS_PORT_NUMBER))
        if whois_srv == 'whois.arin.net':
            s.send(('n ' + target + '\r\n').encode('utf-8'))
        else:
            s.send((target + '\r\n').encode('utf-8'))
        response = ''
        while True:
            d = s.recv(WHOIS_RECEIVE_BUFFER_SIZE)
            if not d:
                break
            response += d.decode('utf-8')
            counter += 1
            if counter == 5:
                break
        s.close()
    except Exception as e:
        print(e)

    return response


def get_whois_nets(data):
    """
    Parses whois data and extracts the Network Ranges returning an array of lists
    where each list has the starting and ending IP of the found range.
    """

    pattern = r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) - ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
    results = re.findall(pattern, data)

    return results


def get_whois_orgname(data):
    org_pattern = r'OrgName\:\s*(.*)\n'
    result = re.findall(org_pattern, data)
    # Let's try RIPENET Format
    if not result:
        org_pattern = r'netname\:\s*(.*)\n'
        result = re.findall(org_pattern, data)
    if not result:
        result.append('Not Found')
    return result
