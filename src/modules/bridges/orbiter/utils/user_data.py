from eth_typing import Address
from web3 import Web3


async def get_wallet_balance(w3: Web3, address: Address) -> float:
    balance = w3.eth.get_balance(address)

    return balance
