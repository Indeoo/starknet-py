from aiohttp import ClientSession
import re

from src.modules.nfts.unframed.utils.requests_data import headers


async def get_item(max_nft_price: float) -> tuple[str, int]:
    async with ClientSession(headers=headers) as session:
        response = await session.get(
            url='https://cloud.argent-api.com/v1/pandora/starknet/mainnet/collection/0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af/nfts',
            params={
                'page': '0',
                'size': '60',
            })
        response_text = await response.json()
        content = response_text['content']
        for item in content:
            token_id = item['tokenId']
            price = float(item['bestListPrice'])
            if price <= int(max_nft_price * 10 ** 18):
                return token_id, int(price)


async def get_owner_address(item_id: int):
    async with ClientSession(headers=headers) as session:
        response = await session.get(
            url=f'https://cloud.argent-api.com/v1/pandora/starknet/mainnet/nft/0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af/{item_id}/order',
            params={
                'side': 'sell',
                'page': '0',
                'size': '32',
            })
        response_text = await response.json()
        content = response_text['content']
        for item in content:
            owner = item['maker']
            owner = re.sub(r'[^0-9a-fA-F]+', '', owner)
            owner = int(owner, 16)
            return owner
