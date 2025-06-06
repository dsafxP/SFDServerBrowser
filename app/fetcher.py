import aiohttp
from app.xml_parser import parse_servers_from_xml

async def fetch_game_servers(callback=None):
    # Define the SOAP request body
    soap_request = """<?xml version='1.0' encoding='utf-8'?>
    <soap12:Envelope xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:soap12='http://www.w3.org/2003/05/soap-envelope'>
        <soap12:Body>
            <GetGameServers xmlns='https://mythologicinteractive.com/Games/SFD/'>
                <validationToken></validationToken>
            </GetGameServers>
        </soap12:Body>
    </soap12:Envelope>"""

    # URL of the SOAP endpoint
    url = "https://mythologicinteractive.com/SFDGameServices.asmx"

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "SOAPAction": "https://mythologicinteractive.com/Games/SFD/GetGameServers",
    }

    # Perform the request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=soap_request, headers=headers) as response:
            if response.status == 200:
                response_text = await response.text()
                servers = parse_servers_from_xml(response_text)

                servers = [server for server in servers if server.version_nr != 0]

                if callback:
                    # Call the provided callback function (GUI update)
                    callback(servers)
                    return None
                else:
                    return servers
            else:
                print(f"Request failed with status code: {response.status}")
                return None
