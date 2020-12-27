#!/usr/bin/env python3

import os
import subprocess
import requests
from jinja2 import Environment, FileSystemLoader

def download_servers():
    res = requests.get("https://api.protonmail.ch/vpn/logicals")
    data = res.json()
    servers = data["LogicalServers"]
    p2p_servers = [server for server in servers if server["Features"] == 4]
    for server in p2p_servers:
        ip_list = [subserver["EntryIP"] for subserver in server["Servers"]]
        udp_ports = [80, 443, 4569, 1194, 5060]
        tcp_ports = [443, 5995, 8443]

        create_config("tcp", ip_list, tcp_ports, server["Domain"] + ".tcp")
        create_config("udp", ip_list, udp_ports, server["Domain"] + ".udp")

def create_config(protocol, serverlist, ports, name):

    # Set specific values
    values = {
            "openvpn_protocol": protocol,
            "serverlist": serverlist,
            "openvpn_ports": ports,
            "split": False,
            "ip_nm_pairs": [],
            "ipv6_disabled": is_ipv6_disabled()
    }

    # Prepare j2 environment
    template_file = "openvpn_template.j2"
    j2 = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")))
    template = j2.get_template(template_file)

    dir_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf-files")
    with open(dir_name + "/" + name + ".ovpn", "w") as f:
        f.write(template.render(values))

def is_ipv6_disabled():
    ipv6_state = subprocess.run(['sysctl', '-n', 'net.ipv6.conf.all.disable_ipv6'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    if ipv6_state.returncode != 0 or int(ipv6_state.stdout):
        return True
    else:
        return False

if __name__ == "__main__":
    download_servers()
