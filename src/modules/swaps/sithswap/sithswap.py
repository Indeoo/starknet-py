from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.cairo import felt

from src.utils.base_liquidity_remove import BaseLiquidityRemove
from src.utils.transaction_data import setup_token_addresses
from src.modules.swaps.utils.tokens import liquidity_tokens
from src.utils.base_liquidity import BaseLiquidity
from src.utils.base_swap import BaseSwap

from src.modules.swaps.sithswap.utils.transaction_data import (
    get_approve_call,
    get_swap_call,
    get_amount_out,
    get_liquidity_call,
    get_liquidity_remove_call,
)


class SithSwap(BaseSwap):
    async def get_contract_address(self) -> felt:
        return 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627

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


class SithSwapLiquidity(BaseLiquidity):
    async def get_contract_address(self) -> felt:
        return 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627

    async def get_swap_instance(self, private_key: felt, token: str, token2: str, amount_from: float,
                                amount_to: float) -> SithSwap:
        return SithSwap(private_key, token.upper(), token2.upper(), amount_from, amount_to, False)

    async def get_calls(self, contract_address: felt, from_token_address: felt, to_token_address: felt, amount: int,
                        stable_amount: int) -> list:
        approve_call_eth: Call = await get_approve_call(contract_address,
                                                        from_token_address,
                                                        amount)
        approve_call_stable: Call = await get_approve_call(
            contract_address,
            to_token_address,
            stable_amount)
        liquidity_call: Call = await get_liquidity_call(
            contract_address,
            self.account,
            amount,
            from_token_address,
            to_token_address,
            stable_amount
        )
        return [approve_call_eth, approve_call_stable, liquidity_call]

    async def get_amount_out(self, amount: int, from_token_address: felt, to_token_address: felt) -> int:
        contract = await Contract.from_address(address=await self.get_contract_address(),
                                               provider=self.account)
        stable_amount = await get_amount_out(amount, contract, from_token_address,
                                             to_token_address)
        return stable_amount


class SithLiquidityRemove(BaseLiquidityRemove):
    async def get_contract_address(self) -> felt:
        return 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627

    async def get_liquidity_token(self) -> felt:
        return liquidity_tokens['SithSwap']['ETH'][self.from_token_pair.upper()]

    async def setup_token_addresses(self) -> tuple[felt, felt]:
        return await setup_token_addresses('ETH', self.from_token_pair)

    async def get_calls(self, contract_address: felt, from_token_address: felt, to_token_address: felt,
                        liquidity_token: felt, amount: int, account: Account) -> list[Call, Call]:
        approve_call: Call = await get_approve_call(contract_address, liquidity_token, amount)
        liquidity_remove_call: Call = await get_liquidity_remove_call(
            contract_address, account, amount, from_token_address, to_token_address
        )
        return [approve_call, liquidity_remove_call]

    async def get_pool_name(self) -> str:
        return 'SithSwap'
