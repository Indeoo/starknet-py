from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.cairo import felt

from src.modules.bridges.orbiter.utils.orbiter_limits import transfer_limit
from .config import contract_orbiter_router
from src.utils.chains import *


async def get_router(token: str) -> str:
    return contract_orbiter_router[token.lower()]


async def get_chain_id(from_chain) -> int:
    chain_mapping = {
        'MATIC': POLYGON.chain_id,
        'ETH': ETH.chain_id,
        'OP': OP.chain_id,
        'BSC': BSC.chain_id,
        'ARB': ARB.chain_id,
        'NOVA': NOVA.chain_id,
        'ERA': ERA.chain_id,
        'LITE': LITE.chain_id
    }
    return chain_mapping.get(from_chain.upper(), 0)


async def get_scan_url(from_chain) -> str:
    url_mapping = {
        'MATIC': POLYGON.scan,
        'ETH': ETH.scan,
        'OP': OP.scan,
        'BSC': BSC.scan,
        'ARB': ARB.scan,
        'NOVA': NOVA.scan,
        'ERA': ERA.scan
    }
    return url_mapping.get(from_chain.upper(), 0)


async def check_eligibility(from_chain: str, to_chain: str, token: str, amount: float) -> tuple[bool, str, str]:
    if token.lower() == 'eth':
        amount = amount / 10 ** 18
    else:
        amount = amount / 10 ** 6

    limits = transfer_limit[from_chain.lower()][to_chain.lower()][token.lower()]

    if limits['max'] >= amount >= limits['min']:
        if limits['min'] <= amount <= limits['min'] + \
                limits['withholding_fee']:
            amount = amount + limits['withholding_fee']
            amount = round(amount, 4)

        if (amount + limits['withholding_fee']) >= limits['max']:
            amount = amount - transfer_limit['withholding_fee']

        return True, limits['min'], limits['max']
    else:
        return False, limits['min'], limits['max']


async def get_approve_call(to_address: felt, value: int) -> Call:
    approve_call = Call(to_addr=to_address,
                        selector=get_selector_from_name('approve'),
                        calldata=[0x0173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b,
                                  int(value * 2),
                                  int(value * 2)])
    return approve_call


async def get_transfer_call(value: int, receiver_address: felt) -> Call:
    transfer_call = Call(to_addr=0x0173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b,
                         selector=get_selector_from_name('transferERC20'),
                         calldata=[
                             0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
                             0x064a24243f2aabae8d2148fa878276e6e6e452e3941b417f3c33b1649ea83e11,
                             value,
                             0,
                             receiver_address])
    return transfer_call
