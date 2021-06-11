"""Functions to manipulate network IPs.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

from netaddr import IPNetwork


def get_all_network_ips(network):
    """Given a network (0.0.0.0/24) return all possible ip addresses

    arg:
        network (str): IP network to extract IP's from

    return (list): IP's in given network
    """
    return [str(ip) for ip in IPNetwork(network)]


def get_all_networks_ips(networks):
    """Given a list of networks return all possible ip addresses.

    arg:
        networks (list): List of IP networks to extract IP's from

    return (list): [ ['IP', 'Network'], ['IP2', 'Network'] ]
    """
    final_list = []
    for network in networks:
        ips = get_all_network_ips(network)
        final = [[ip, network] for ip in ips]
        final_list = final_list + final
    return final_list
