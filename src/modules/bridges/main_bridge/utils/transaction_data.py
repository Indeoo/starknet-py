from web3.contract import Contract
from web3 import Web3
from src.utils.transaction_data import load_abi


async def get_contract(web3: Web3) -> Contract:
    return web3.eth.contract(address=Web3.to_checksum_address('0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'),
                             abi=await load_abi('main_bridge'))

