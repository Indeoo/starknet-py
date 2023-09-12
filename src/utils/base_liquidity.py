from asyncio import sleep
from typing import Any
import random
import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET
from starknet_py.cairo import felt
from loguru import logger

from starknet_py.net.signer.stark_curve_signer import (
    StarkCurveSigner,
    KeyPair,
)

from src.utils.retry import retry

from config import (
    ESTIMATED_FEE_MULTIPLIER,
    MAX_FEE_FOR_TRANSACTION,
    RPC_URL,
    WALLET_TYPE,
)
from src.utils.transaction_data import (
    get_balance,
    setup_token_addresses,
    create_amount,
)


class BaseLiquidity:
    def __init__(self, private_key: str, token: str, token2: str, amount_from: float, amount_to: float) -> None:
        self.private_key = private_key
        private_key = re.sub(r'[^0-9a-fA-F]+', '', private_key)
        private_key = int(private_key, 16)
        if WALLET_TYPE.lower() == 'argent':
            proxy_class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
            implementation_class_hash = 0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
        elif WALLET_TYPE.lower() == 'braavos':
            proxy_class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            implementation_class_hash = 0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570
        else:
            logger.error(f'Unknown wallet type {WALLET_TYPE} | Use only: argent/braavos.')
            return
        if WALLET_TYPE.lower() == 'argent':
            selector = get_selector_from_name("initialize")
        else:
            selector = get_selector_from_name("initializer")
        key_pair = KeyPair.from_private_key(private_key)
        if WALLET_TYPE == 'argent':
            calldata = [key_pair.public_key, 0]
        else:
            calldata = [key_pair.public_key]
        address = compute_address(class_hash=proxy_class_hash,
                                  constructor_calldata=[implementation_class_hash, selector, len(calldata), *calldata],
                                  salt=key_pair.public_key)
        self.account = Account(
            address=address,
            client=FullNodeClient(
                node_url=RPC_URL) if RPC_URL != 'https://alpha-mainnet.starknet.io' else GatewayClient(net=MAINNET),
            signer=StarkCurveSigner(
                account_address=address,
                key_pair=key_pair,
                chain_id=StarknetChainId.MAINNET
            )
        )
        self.token = token
        self.token2 = token2
        self.amount = round(random.uniform(amount_from, amount_to), 6)

    @retry()
    async def add_liquidity(self) -> None:
        contract_address = await self.get_contract_address()
        from_token_address, to_token_address = await setup_token_addresses(self.token, self.token2)
        amount = await create_amount(18 if self.token.lower() == 'eth' else 6, self.amount)

        eth_balance = await get_balance(from_token_address, self.account)
        if amount > eth_balance:
            logger.error(f'Not enough ETH balance {hex(self.account.address)}')
            return

        while True:
            stable_balance = await get_balance(to_token_address, self.account)
            stable_amount = await self.get_amount_out(amount, from_token_address, to_token_address)
            if stable_amount > stable_balance:
                logger.error(f'Not enough {self.token2.upper()} balance {hex(self.account.address)}')
                logger.info(f'Swapping {self.amount} ETH => {self.token2.upper()}')
                swap = await self.get_swap_instance(self.private_key, self.token, self.token2, self.amount, self.amount)
                await swap.swap()
                sleep_time = random.randint(30, 60)
                logger.info(f'Sleeping {sleep_time} seconds...')
                await sleep(sleep_time)
                continue
            break

        calls = await self.get_calls(contract_address, from_token_address, to_token_address, amount, stable_amount)

        while True:
            self.account.ESTIMATED_FEE_MULTIPLIER = ESTIMATED_FEE_MULTIPLIER
            invoke_tx = await self.account.sign_invoke_transaction(calls=calls, auto_estimate=True)
            estimate_fee = await self.account._estimate_fee(invoke_tx)
            if estimate_fee.overall_fee / 10 ** 18 > MAX_FEE_FOR_TRANSACTION:
                logger.info('Current fee is too high...')
                sleep_time = random.randint(45, 75)
                logger.info(f'Sleeping {sleep_time} seconds')
                await sleep(sleep_time)
                continue
            tx = await self.account.client.send_transaction(invoke_tx)
            logger.debug(f'Transaction sent. Waiting... TX: https://voyager.online/tx/{hex(tx.transaction_hash)}')
            await sleep(15)
            await self.account.client.wait_for_tx(tx.transaction_hash)
            logger.success(
                f'Successfully added liquidity with {self.amount} ETH, {stable_amount / 10 ** 6} {self.token2.upper()} | TX: https://voyager.online/tx/{hex(tx.transaction_hash)}')
            break

    async def get_contract_address(self) -> None:
        raise NotImplementedError("Subclasses must implement get_contract_address()")

    async def get_swap_instance(self, private_key: felt, token: str, token2: str, amount_from: float,
                                amount_to: float) -> Any:
        raise NotImplementedError("Subclasses must implement get_swap_instance()")

    async def get_calls(self, contract_address: felt, from_token_address: felt, to_token_address: felt, amount: int,
                        stable_amount: int) -> None:
        raise NotImplementedError("Subclasses must implement get_calls()")

    async def get_amount_out(self, amount: int, from_token_address: felt, to_token_address: felt) -> None:
        raise NotImplementedError("Subclasses must implement get_amount_out()")
