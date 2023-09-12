from starknet_py.net.account.account import Account

from starknet_py.net.client_models import Call
from starknet_py.cairo import felt

from src.utils.base_swap import BaseSwap

from src.modules.swaps.fibrous_swap.utils.transaction_data import (
    get_approve_call,
    get_swap_call,
)


class FibrousSwap(BaseSwap):
    async def get_contract_address(self) -> felt:
        contract = 0x1b23ed400b210766111ba5b1e63e33922c6ba0c45e6ad56ce112e5f4c578e62
        return contract

    async def get_approve_call(self, from_token_address: felt, contract_address: felt, amount: int) -> Call:
        approve_call = await get_approve_call(contract_address,
                                              from_token_address,
                                              amount)
        return approve_call

    async def get_swap_call(self, contract_address: felt, account: Account, from_token_address: felt,
                            to_token_address: felt, amount: int) -> Call:
        swap_call = await get_swap_call(
            contract_address,
            account,
            amount,
            from_token_address,
            to_token_address,
        )
        return swap_call
