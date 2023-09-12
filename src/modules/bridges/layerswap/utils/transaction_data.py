import json

from aiohttp import ClientSession
from asyncio import run
from src.modules.bridges.layerswap.utils.request_data import event_headers, token_headers


async def send_request(url: str, headers, data: dict):
    async with ClientSession(headers=headers) as session:
        response = await session.post(url=url, data=data)
        response_text = await response.text()
    return response_text


async def send_token_request() -> str:
    response_text = await send_request(url='https://identity-api.layerswap.io/connect/token', headers=token_headers,
                                       data={
                                           'client_id': 'layerswap_bridge_ui',
                                           'grant_type': 'credentialless',
                                       })
    return response_text


async def get_swaps(headers):
    response_text = await send_request(url='https://bridge-api.layerswap.io//api/swaps', headers=headers,
                                  data={
                                      'amount': 2,
                                      'source': 'ARBITRUM_MAINNET',
                                      'destination': 'STARKNET_MAINNET',
                                      'asset': 'ETH',
                                      'source_address': '0xF7DceCf6C7f74bcc25471669A712e89C5b2e5515',
                                      'destination_address': '0x4af0a2452feee7d2602735f7c7829af868ac67873bad6eb4bee9982afcebfce',
                                      'refuel': False,
                                  })
    return response_text


async def get_address_request(headers):
    response_text = await send_request(url='https://bridge-api.layerswap.io//api/deposit_addresses/ZKSYNCERA_MAINNET',
                                       headers=headers, data=None)
    return response_text


async def complete():
    token_request_text = json.loads(await send_token_request())
    access_token = token_request_text['access_token']
    headers = {
        'authority': 'bridge-api.layerswap.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9,ru-RU;q=0.8,en-US;q=0.7',
        'access-control-allow-origin': '*',
        'authorization': f'Bearer {access_token}',
        # 'content-length': 'text/plain',
        'origin': 'https://www.layerswap.io',
        'referer': 'https://www.layerswap.io/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    swaps = await get_swaps(headers)
    print(swaps)
    address = await get_address_request(headers)
    print(address)


def main():
    run(complete())


main()
