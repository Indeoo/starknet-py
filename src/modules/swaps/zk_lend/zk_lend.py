import asyncio
from asyncio import sleep
import random
import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from loguru import logger

from starknet_py.net.signer.stark_curve_signer import (
    StarkCurveSigner,
    KeyPair,
)
from web3 import Web3

from src.modules.swaps.utils.tokens import tokens

from config import (
    ESTIMATED_FEE_MULTIPLIER,
    MAX_FEE_FOR_TRANSACTION,
    WALLET_TYPE,
    RPC_URL,
)

from src.modules.swaps.zk_lend.utils.transaction_data import (
    get_approve_call,
    get_deposit_call,
    get_collateral_call,
    get_withdraw_call, get_withdraw_all_call,
)

from src.utils.transaction_data import (
    get_balance,
    create_amount,
)


class ZKLendLiquidity:
    def __init__(self) -> None:
        self.private_key = None
        self.token = None
        self.amount_interval = None
        self.min_amount_interval = None

    async def initialize(self, private_key: str, token: str, amount_interval, min_amount_interval):
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
        account = Account(
            address=address,
            client=FullNodeClient(node_url=RPC_URL),
            signer=StarkCurveSigner(
                account_address=address,
                key_pair=key_pair,
                chain_id=StarknetChainId.MAINNET
            )
        )

        if amount_interval == 'all_balance':

            token_address = tokens[token.upper()]
            balance = await get_balance(token_address, account)
            amount = float(Web3().from_wei(balance, 'ether')) - round(
                random.uniform(min_amount_interval['from'], min_amount_interval['to']), 6)
        else:
            amount = round(random.uniform(amount_interval['from'], amount_interval['to']), 6)

        self.account = account
        self.token = token
        self.amount = amount
        self.contract_address = 0x4c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05

    async def add_liquidity(self) -> None:
        token_address = tokens[self.token.upper()]
        amount = await create_amount(18 if self.token.lower() == 'eth' else 6, self.amount)
        balance = await get_balance(token_address, self.account)

        if amount > balance:
            logger.error(f'Not enough {self.token.upper()} balance {hex(self.account.address)}')
            return

        approve_call = await get_approve_call(contract_address=self.contract_address, to_address=token_address,
                                              value=amount)
        deposit_call = await get_deposit_call(contract_address=self.contract_address, value=amount,
                                              from_token_address=token_address)
        collateral_call = await get_collateral_call(contract_address=self.contract_address,
                                                    from_token_address=token_address)
        calls = [approve_call, deposit_call, collateral_call]

        retries = 0
        while retries < 3:
            try:
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
                    f'Successfully added liquidity with {self.amount} {self.token} | TX: https://voyager.online/tx/{hex(tx.transaction_hash)}')
                break
            except Exception as ex:
                retries += 1
                logger.error(f'Something went wrong {ex}')
                logger.debug('Trying one more time')
                time_sleep = random.randint(40, 60)
                logger.debug(f'Sleeping {time_sleep} seconds...')
                await sleep(time_sleep)
                continue


class ZKLendLiquidityRemove:
    def __init__(self, private_key: str, token: str, remove_all: bool, removing_percentage: float) -> None:
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
            client=FullNodeClient(node_url=RPC_URL),
            signer=StarkCurveSigner(
                account_address=address,
                key_pair=key_pair,
                chain_id=StarknetChainId.MAINNET
            )
        )
        self.token = token
        self.contract_address = 0x4c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05
        self.remove_all = remove_all
        self.removing_percentage = removing_percentage

    async def remove_liquidity(self) -> None:
        liquidity_token_address = tokens[self.token]
        balance = await get_balance(liquidity_token_address, self.account)
        if balance == 0:
            logger.error("Looks like you don't have any liquidity to remove")
            return
        if self.remove_all is True:
            withdraw_call = await get_withdraw_all_call(self.contract_address, liquidity_token_address)
        else:
            amount = int(balance * self.removing_percentage)
            withdraw_call = await get_withdraw_call(self.contract_address, liquidity_token_address, amount)

        calls = [withdraw_call]

        retries = 0
        while retries < 3:
            try:
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
                    f'Removed {"all" if self.remove_all else f"{self.removing_percentage * 100}%"} tokens from ZkLend pool |  TX: https://voyager.online/tx/{hex(tx.transaction_hash)}')
                break
            except Exception as ex:
                retries += 1
                if 'assert_not_zero' in str(ex):
                    logger.error("Looks like you don't have any tokens to withdraw")
                    return
                logger.error(f'Something went wrong {ex}')
                logger.debug('Trying one more time')
                time_sleep = random.randint(40, 60)
                logger.debug(f'Sleeping {time_sleep} seconds...')
                await sleep(time_sleep)
                continue
