from fractions import Fraction
from hexbytes import HexBytes
from asyncio import sleep
import random
import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from loguru import logger
from web3 import Web3

from starknet_py.net.signer.stark_curve_signer import (
    KeyPair,
    StarkCurveSigner
)

from src.modules.bridges.orbiter.utils.user_data import get_wallet_balance
from src.modules.bridges.orbiter.utils.config import chain_without_eipstandart

from config import (
    ESTIMATED_FEE_MULTIPLIER,
    MAX_FEE_FOR_TRANSACTION,
    RPC_URL,
)

from src.utils.transaction_data import (
    get_balance,
    load_abi,
)

from src.modules.bridges.orbiter.utils.transaction_data import (
    get_approve_call,
    get_transfer_call,
    check_eligibility,
    get_chain_id,
    get_scan_url,
)


class OrbiterBridgeWithdraw:
    def __init__(self,
                 private_key: str,
                 chain: str,
                 receiver_address: str,
                 amount_from: float,
                 amount_to: float,
                 bridge_all_balance: bool,
                 code: int
                 ) -> None:
        private_key = re.sub(r'[^0-9a-fA-F]+', '', private_key)
        private_key = int(private_key, 16)
        self.receiver_address = re.sub(r'[^0-9a-fA-F]+', '', receiver_address)
        self.receiver_address = int(receiver_address, 16)
        proxy_class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
        implementation_class_hash = 0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
        selector = get_selector_from_name("initialize")
        key_pair = KeyPair.from_private_key(private_key)
        calldata = [key_pair.public_key, 0]
        address = compute_address(class_hash=proxy_class_hash,
                                  constructor_calldata=[implementation_class_hash, selector, len(calldata),
                                                        *calldata],
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
        self.chain = chain
        self.amount = round(random.uniform(amount_from, amount_to), 6)
        self.bridge_all_balance = bridge_all_balance
        self.code = code

    async def withdraw(self) -> None:
        balance = await get_balance(0x049D36570D4e46f48e99674bd3fcc84644DdD6b96F7C741B1562B82f9e004dC7, self.account)
        if self.bridge_all_balance is True:
            amount = balance // 10 ** 13 * 10 ** 13
        else:
            amount = int(self.amount * 10 ** 18)

        if amount > balance:
            logger.error(f'Not enough balance for wallet {hex(self.account.address)}')

        amount = int(str(Fraction(amount))[:-4] + str(self.code))

        approve_call = await get_approve_call(0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
                                              amount)
        transfer_call = await get_transfer_call(amount, self.receiver_address)
        calls = [approve_call, transfer_call]
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
                    f'Successfully bridged {"all" if self.bridge_all_balance is True else self.amount} ETH tokens => {self.chain} TX: https://voyager.online/tx/{hex(tx.transaction_hash)}'
                )
                break
            except Exception as ex:
                retries += 1
                logger.error(f'Something went wrong {ex}')
                logger.debug('Trying one more time')
                time_sleep = random.randint(40, 60)
                logger.debug(f'Sleeping {time_sleep} seconds...')
                await sleep(time_sleep)
                continue


class OrbiterBridgeDeposit:
    def __init__(self,
                 private_key: str,
                 receiver_address: str,
                 rpc_chain: str,
                 bridge_contract: str,
                 chain: str,
                 amount_from: float,
                 amount_to: float,
                 code: int,
                 ) -> None:
        self.private_key = private_key
        self.receiver_address = receiver_address
        self.bridge_contract = bridge_contract
        self.chain = chain
        self.amount = round(random.uniform(amount_from, amount_to), 7)
        self.code = code
        self.web3 = Web3(Web3.HTTPProvider(rpc_chain))
        self.eth_account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.eth_account.address
        self.nonce = self.web3.eth.get_transaction_count(self.address_wallet)

    async def deposit(self) -> None:
        amount = int(self.amount * 10 ** 18)
        amount = int(str(Fraction(amount))[:-4] + str(self.code))

        balance = await get_wallet_balance(self.web3, self.address_wallet)

        eligibility, min_limit, max_limit = await check_eligibility(self.chain, 'STARKNET', 'ETH', amount)

        if not eligibility:
            logger.error(f'Limits error | Min: {min_limit}, Max: {max_limit}')
            return

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.address_wallet}')
            return

        contract = self.web3.eth.contract(address=Web3.to_checksum_address(self.bridge_contract),
                                          abi=await load_abi('orbiter'))

        tx = contract.functions.transfer(
            Web3.to_checksum_address(Web3.to_checksum_address('0x80C67432656d59144cEFf962E8fAF8926599bCF8')),
            HexBytes('0x03' +
                     self.receiver_address[2:])).build_transaction({
            "chainId": await get_chain_id(self.chain),
            'value': amount,
            'nonce': self.nonce
        })

        if not self.chain.lower() in chain_without_eipstandart:
            tx.update({'maxFeePerGas': self.web3.eth.gas_price})
            tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})
        else:
            tx.update({'gasPrice': self.web3.eth.gas_price})

        if self.chain.lower() == 'op':
            tx.update({'from': self.address_wallet})

        scan_url = await get_scan_url(self.chain)
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(self.web3.keccak(signed_tx.rawTransaction))
        logger.success(
            f'Successfully bridged {self.amount} ETH from {self.chain.upper()} => Starknet | Transaction: {scan_url}/{tx_hash}')
