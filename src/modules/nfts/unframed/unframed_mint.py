from asyncio import sleep
import random
import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.cairo import felt
from loguru import logger
from starknet_py.net.networks import MAINNET

from starknet_py.net.signer.stark_curve_signer import (
    StarkCurveSigner,
    KeyPair,
)
from src.modules.nfts.unframed.utils.transaction_data import get_increase_allowance_call, get_purchase_call
from src.modules.nfts.unframed.utils.collection_parser import get_item, get_owner_address
from config import (
    MAX_FEE_FOR_TRANSACTION,
    ESTIMATED_FEE_MULTIPLIER,
    RPC_URL,
)

from src.utils.transaction_data import (
    setup_token_addresses,
    create_amount,
    get_balance,
)


class UnframedMint:
    def __init__(self,
                 private_key: str,
                 max_nft_price: float
                 ) -> None:
        private_key = re.sub(r'[^0-9a-fA-F]+', '', private_key)
        private_key = int(private_key, 16)
        proxy_class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
        implementation_class_hash = 0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
        selector = get_selector_from_name("initialize")
        key_pair = KeyPair.from_private_key(private_key)
        calldata = [key_pair.public_key, 0]
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
        self.contract_address = 0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b
        self.max_nft_price = max_nft_price

    async def mint(self) -> None:
        item_id, price = await get_item(self.max_nft_price)
        owner_address = await get_owner_address(item_id)

        increase_allowance_call = await get_increase_allowance_call(self.contract_address,
                                                                    0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
                                                                    price)
        purchase_call = await get_purchase_call(self.contract_address, price, item_id, owner_address, self.account)

        calls = [increase_allowance_call, purchase_call]
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
                    f'Successfully minted NTF | TX: https://voyager.online/tx/{hex(tx.transaction_hash)}'
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
