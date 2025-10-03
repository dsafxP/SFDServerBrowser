import xml.etree.ElementTree as Et

from core.server import Server


def parse_servers_from_xml(response_text):
    """
    This function parses the XML response and converts it into a list of Server objects.
    """
    # Parse the XML response
    root = Et.fromstring(response_text)

    # Define namespaces to access elements
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'sfd': 'https://mythologicinteractive.com/Games/SFD/'
    }

    servers_element = root.find('.//sfd:GetGameServersResult/sfd:Servers', namespaces)

    servers = []
    if servers_element is not None:
        for server_element in servers_element.findall('sfd:SFDGameServer', namespaces):
            # Helper function to safely get and convert values
            def get_text(tag, default=None, convert_func=None):
                value = server_element.findtext(f'sfd:{tag}', default=default, namespaces=namespaces)
                if value is None or value == default:
                    return default
                return convert_func(value) if convert_func else value

            # Create Server object using keyword arguments (works with dataclass)
            server = Server(
                # Required fields
                address_ipv4=get_text('AddressIPv4', ''),
                port=get_text('Port', 0, int),

                # Optional fields with defaults
                address_ipv6=get_text('AddressIPv6'),
                lip=get_text('LIP'),
                game_name=get_text('GameName', ''),
                game_mode=get_text('GameMode', 0, int),
                map_name=get_text('MapName', ''),
                players=get_text('Players', 0, int),
                max_players=get_text('MaxPlayers', 0, int),
                bots=get_text('Bots', 0, int),
                has_password=get_text('HasPassword', 'false').lower() == 'true',
                description=get_text('Description', ''),
                version=get_text('Version', ''),
                version_nr=get_text('VersionNr', 0, int),
                application_instance=get_text('ApplicationInstance')
            )

            servers.append(server)

    return servers