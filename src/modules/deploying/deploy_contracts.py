import re

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET
from loguru import logger

from starknet_py.net.signer.stark_curve_signer import (
    KeyPair,
    StarkCurveSigner,
)

from config import RPC_URL, ESTIMATED_FEE_MULTIPLIER


class DeployContracts:
    def __init__(self,
                 private_key: str,
                 ) -> None:
        private_key = re.sub(r'[^0-9a-fA-F]+', '', private_key)
        private_key = int(private_key, 16)
        self.proxy_class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
        self.implementation_class_hash = 0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
        selector = get_selector_from_name("initialize")
        self.key_pair = KeyPair.from_private_key(private_key)
        calldata = [self.key_pair.public_key, 0]
        self.address = compute_address(class_hash=self.proxy_class_hash,
                                       constructor_calldata=[self.implementation_class_hash, selector, len(calldata),
                                                             *calldata],
                                       salt=self.key_pair.public_key)

        self.account = Account(
            client=GatewayClient(net=MAINNET),
            address=self.address,
            signer=StarkCurveSigner(self.address,
                                    self.key_pair,
                                    StarknetChainId.MAINNET)
        )

    async def deploy_contract(self) -> None:
        self.account.ESTIMATED_FEE_MULTIPLIER = ESTIMATED_FEE_MULTIPLIER
        account_deployment_result = await Account.deploy_account(
            address=self.address,
            class_hash=self.proxy_class_hash,
            salt=self.key_pair.public_key,
            key_pair=self.key_pair,
            client=FullNodeClient(
                node_url=RPC_URL) if RPC_URL != 'https://alpha-mainnet.starknet.io' else GatewayClient(net=MAINNET),
            chain=StarknetChainId.MAINNET,
            constructor_calldata=[self.implementation_class_hash, get_selector_from_name("initialize"), 1,
                                  self.key_pair.public_key],
            auto_estimate=True,
        )
        await account_deployment_result.wait_for_acceptance()
        logger.success(f'Successfully deployed {hex(self.account.address)} wallet')
