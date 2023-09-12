import random
import re

from web3 import Web3

from src.modules.bridges.main_bridge.utils.transaction_data import get_contract
from src.utils.chains import ETH


class MainBridge:
    def __init__(self,
                 private_key: str,
                 receiver_address: str,
                 amount_from: float,
                 amount_to: float,
                 ) -> None:
        self.private_key = private_key
        self.receiver_address = receiver_address
        self.receiver_address = re.sub(r'[^0-9a-fA-F]+', '', receiver_address)
        self.receiver_address = int(self.receiver_address, 16)
        self.amount = round(random.uniform(amount_from, amount_to), 7)

        self.web3 = Web3(Web3.HTTPProvider(ETH.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address

    async def deposit(self) -> None:
        amount = int(self.amount * 10 ** 18)
        amount = int(0.042 * 10 ** 18)
        amount = hex(amount)[2:]
        print(self.receiver_address)
        receiver_address = '0x04AF0a2452fEEE7d2602735f7c7829aF868AC67873bad6EB4beE9982AFCeBFCE'
        tx = {
            'value': amount,
            'to': Web3.to_checksum_address('0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'),
            'data': f'0xe2bbb15800000000000000000000000000000000000000000000000000{amount}{receiver_address[2:]}',
            'chainId': self.web3.eth.chain_id,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            'gasPrice': self.web3.eth.gas_price,
            'gas': 1,
        }
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})
        print(tx)

    async def withdraw(self) -> None:
        pass
