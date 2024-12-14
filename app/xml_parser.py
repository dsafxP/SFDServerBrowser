# app/xml_parser.py
import xml.etree.ElementTree as ET
from .server import Server

def parse_servers_from_xml(response_text):
    """
    This function parses the XML response and converts it into a list of Server objects.
    """
    # Parse the XML response
    root = ET.fromstring(response_text)

    # Define namespaces to access elements
    namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/', 'sfd': 'https://mythologicinteractive.com/Games/SFD/'}
    servers_element = root.find('.//sfd:GetGameServersResult/sfd:Servers', namespaces)

    servers = []
    if servers_element is not None:
        for server_element in servers_element.findall('sfd:SFDGameServer', namespaces):
            # Extract values for each field
            address_ipv4 = server_element.findtext('sfd:AddressIPv4', default=None, namespaces=namespaces)
            address_ipv6 = server_element.findtext('sfd:AddressIPv6', default=None, namespaces=namespaces)
            lip = server_element.findtext('sfd:LIP', default=None, namespaces=namespaces)
            port = int(server_element.findtext('sfd:Port', default=0, namespaces=namespaces))
            game_name = server_element.findtext('sfd:GameName', default=None, namespaces=namespaces)
            game_mode = int(server_element.findtext('sfd:GameMode', default=0, namespaces=namespaces))
            map_name = server_element.findtext('sfd:MapName', default=None, namespaces=namespaces)
            players = int(server_element.findtext('sfd:Players', default=0, namespaces=namespaces))
            max_players = int(server_element.findtext('sfd:MaxPlayers', default=0, namespaces=namespaces))
            bots = int(server_element.findtext('sfd:Bots', default=0, namespaces=namespaces))
            has_password = server_element.findtext('sfd:HasPassword', default='false', namespaces=namespaces) == 'true'
            description = server_element.findtext('sfd:Description', default=None, namespaces=namespaces)
            version = server_element.findtext('sfd:Version', default=None, namespaces=namespaces)
            version_nr = int(server_element.findtext('sfd:VersionNr', default=0, namespaces=namespaces))
            application_instance = server_element.findtext('sfd:ApplicationInstance', default=None, namespaces=namespaces)

            # Create a Server object and append it to the list
            server = Server(address_ipv4, address_ipv6, lip, port, game_name, game_mode, map_name, players, max_players, bots, has_password, description, version, version_nr, application_instance)
            servers.append(server)

    return servers
