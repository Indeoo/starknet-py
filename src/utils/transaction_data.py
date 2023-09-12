from pathlib import Path
import json

from starknet_py.net.account.account import Account
from starknet_py.contract import Contract
from starknet_py.cairo import felt

from src.modules.swaps.utils.tokens import tokens


async def load_abi(name: str) -> list:
    current_dir = Path(__file__).resolve().parent.parent.parent
    abi_path = current_dir / 'assets' / 'abi' / f'{name}.json'
    with open(abi_path) as f:
        abi: list = json.load(f)
    return abi


async def load_contract(contract_address: felt, account: Account) -> Contract:
    contract = await Contract.from_address(
        address=contract_address,
        provider=account,
    )
    return contract


async def create_amount(decimals: int, value: float) -> int:
    return int(value * 10 ** decimals)


async def get_balance(from_address: felt, account: Account) -> int:
    balance = await account.get_balance(from_address)
    return balance


async def setup_token_addresses(from_token: str, to_token: str) -> tuple[felt, felt]:
    from_token_address = tokens[from_token.upper()]
    to_token_address = tokens[to_token.upper()]
    return from_token_address, to_token_address
