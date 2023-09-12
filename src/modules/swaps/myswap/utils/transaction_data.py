from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.contract import Contract
from starknet_py.cairo import felt
from loguru import logger

from config import SLIPPAGE
from src.modules.swaps.myswap.utils.pools import pools
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
    approve_call = Call(to_addr=to_address,
                        selector=get_selector_from_name('approve'),
                        calldata=[int(contract_address), int(value), 0])
    return approve_call


async def get_swap_call(contract_address: felt, account: Account, value: int, from_token_address: felt,
                        to_token_address: felt, from_token: str, to_token: str) -> Call:
    amount_out = await get_amount_out(value, account, from_token_address, to_token_address)
    if from_token.lower() == 'eth' and to_token.lower() == 'usdc' or from_token.lower() == 'usdc' and to_token.lower() == 'eth':
        pool_id = 1
    elif from_token.lower() == 'dai' and to_token.lower() == 'eth' or from_token.lower() == 'eth' and to_token.lower() == 'dai':
        pool_id = 2
    elif from_token.lower() == 'wbtc' and to_token.lower() == 'usdc' or from_token.lower() == 'usdc' and to_token.lower() == 'wbtc':
        pool_id = 3
    elif from_token.lower() == 'eth' and to_token.lower() == 'usdt' or from_token.lower() == 'usdt' and to_token.lower() == 'eth':
        pool_id = 4
    elif from_token.lower() == 'usdt' and to_token.lower() == 'usdc' or from_token.lower() == 'usdc' and to_token.lower() == 'usdt':
        pool_id = 5
    elif from_token.lower() == 'dai' and to_token.lower() == 'usdc' or from_token.lower() == 'usdc' and to_token.lower() == 'dai':
        pool_id = 6
    else:
        logger.error(f'MySwap | Pool not found...')
        return
    swap_call = Call(to_addr=contract_address,
                     selector=get_selector_from_name('swap'),
                     calldata=[
                         pool_id,
                         from_token_address,
                         value,
                         0,
                         int(amount_out * (1 - SLIPPAGE)),
                         0,
                     ])

    return swap_call


async def get_liquidity_call(contract_address: felt, account: Account, value: int, from_token_address: felt,
                             to_token_address: felt, amount_out: int) -> Call:
    swap_call = Call(to_addr=contract_address,
                     selector=get_selector_from_name("add_liquidity"),
                     calldata=[
                         from_token_address,
                         value,
                         0,
                         int(value * (1 - SLIPPAGE)),
                         0,
                         to_token_address,
                         amount_out,
                         0,
                         int(amount_out * (1 - SLIPPAGE)),
                         0,
                     ])
    return swap_call


async def get_liquidity_remove_call(contract_address: felt, value: int, pool_id: int) -> Call:
    remove_call = Call(to_addr=contract_address,
                       selector=get_selector_from_name("withdraw_liquidity"),
                       calldata=[
                           pool_id,
                           value,
                           0,
                           0,
                           0,
                           0,
                           0
                       ])
    return remove_call


async def get_pool_id(from_token: str, to_token: str) -> int:
    return pools[from_token.upper()][to_token.upper()]
