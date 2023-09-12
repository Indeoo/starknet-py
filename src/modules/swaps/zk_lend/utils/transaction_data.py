from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.cairo import felt


async def get_approve_call(contract_address: felt, to_address: felt, value: int) -> Call:
    return Call(to_addr=to_address,
                selector=get_selector_from_name('approve'),
                calldata=[int(contract_address), int(value), 0])


async def get_collateral_call(contract_address: felt, from_token_address: felt) -> Call:
    return Call(to_addr=contract_address,
                selector=get_selector_from_name('enable_collateral'),
                calldata=[from_token_address])


async def get_deposit_call(contract_address: felt, value: int, from_token_address: felt) -> Call:
    deposit_call = Call(to_addr=contract_address,
                        selector=get_selector_from_name("deposit"),
                        calldata=[
                            from_token_address,
                            value,
                        ])
    return deposit_call


async def get_withdraw_call(contract_address: felt, from_token_address: felt, amount: int) -> Call:
    withdraw_call = Call(to_addr=contract_address,
                         selector=get_selector_from_name("withdraw"),
                         calldata=[
                             from_token_address,
                             amount,
                         ])
    return withdraw_call


async def get_withdraw_all_call(contract_address: felt, from_token_address: felt) -> Call:
    withdraw_call = Call(to_addr=contract_address,
                         selector=get_selector_from_name("withdraw_all"),
                         calldata=[
                             from_token_address,
                         ])
    return withdraw_call
