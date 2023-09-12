from starknet_py.cairo import felt
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call

from src.utils.base_swap import BaseSwap

from src.modules.swaps.anvuswap.utils.transaction_data import (
    get_approve_call,
    get_swap_call,
)


class AnvuSwap(BaseSwap):
    async def get_contract_address(self) -> felt:
        return 0x4270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f

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
