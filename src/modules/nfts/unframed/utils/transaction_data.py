from time import time

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.contract import Contract
from starknet_py.cairo import felt

from config import SLIPPAGE
from src.utils.transaction_data import (
    load_abi
)


async def get_increase_allowance_call(contract_address: felt, to_address: felt, value: int) -> Call:
    increase_allowance_call = Call(to_addr=to_address,
                                   selector=get_selector_from_name('increaseAllowance'),
                                   calldata=[int(contract_address), int(value), 0])
    return increase_allowance_call


async def get_purchase_call(contract_address: felt, price: int, item_id: int, owner_address: int, account: Account) -> Call:

    purchase_call = Call(to_addr=contract_address,
                         selector=get_selector_from_name('execute_taker_buy'),
                         calldata=[
                             price,

                             1000,

                             owner_address,
                             price,

                             item_id,

                             0x012f3e256a78d411730c30d4ace443e31a59b1d48340d888d7aa198a2c4311f8,
                             0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,

                             int(time()),
                             int(time() + 100),
                             1000,

                         ])
    return purchase_call
