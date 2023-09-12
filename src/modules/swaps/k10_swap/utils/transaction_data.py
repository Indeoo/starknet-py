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


async def get_amount_out(amount: int, account: Account, from_token_address: felt, to_token_address: felt) -> int:
    contract = Contract(address=0x41fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023,
                        abi=await load_abi('jediswap'),
                        provider=account)
    tx = await contract.functions['get_amounts_out'].prepare(
        amountIn=amount,
        path=[
            from_token_address,
            to_token_address,
        ]
    ).call()
    return int(tx.amounts[1])


async def get_approve_call(contract_address: felt, to_address: felt, value: int) -> Call:
    return Call(to_addr=to_address,
                selector=get_selector_from_name('approve'),
                calldata=[int(contract_address), int(value), 0])


async def get_swap_call(contract_address: felt, account: Account, value: int, from_token_address: felt,
                        to_token_address: felt) -> Call:

    amount_out = await get_amount_out(value, account, from_token_address, to_token_address)
    swap_call = Call(to_addr=contract_address,
                     selector=get_selector_from_name('swapExactTokensForTokens'),
                     calldata=[
                         value,
                         0,
                         int(amount_out * (1-SLIPPAGE)),
                         0,
                         2,
                         from_token_address,
                         to_token_address,
                         account.address,
                         int(time() + 4000)
                     ])

    return swap_call


async def get_liquidity_call(contract_address: felt, account: Account, value: int, from_token_address: felt,
                             to_token_address: felt, amount_out: int) -> Call:
    swap_call = Call(to_addr=contract_address,
                     selector=get_selector_from_name("addLiquidity"),
                     calldata=[
                         from_token_address,
                         to_token_address,
                         value,
                         0,
                         amount_out,
                         0,
                         int(value * (1 - SLIPPAGE)),
                         0,
                         int(amount_out * (1 - SLIPPAGE)),
                         0,
                         account.address,
                         int(time() + 4000)
                     ])
    return swap_call


async def get_liquidity_remove_call(contract_address: felt, account: Account, value: int,
                                    from_token_address: felt, to_token_address: felt) -> Call:
    remove_call = Call(to_addr=contract_address,
                       selector=get_selector_from_name("removeLiquidity"),
                       calldata=[
                           from_token_address,
                           to_token_address,
                           value,
                           0,
                           0,
                           0,
                           0,
                           0,
                           account.address,
                           int(time() + 4000)
                       ])
    return remove_call
