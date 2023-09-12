import random

from loguru import logger
import ccxt

from okx_data.okx_data import proxy
from src.modules.okx_withdraw.utils.data import get_withdrawal_fee


class OkxWithdraw:
    def __init__(self, api_key: str, api_secret: str, passphrase: str, amount_from: float, amount_to: float,
                 receiver_address: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.amount_from = amount_from
        self.amount_to = amount_to
        self.receiver_address = receiver_address
        self.amount = round(random.uniform(self.amount_from, self.amount_to), 6)

    async def withdraw(self) -> None:
        exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'enableRateLimit': True,
            'proxies': {
                'http': proxy,
                'https': proxy
            },
        })

        try:
            chain_name = 'ETH' + '-' + 'StarkNet'
            fee = await get_withdrawal_fee('ETH', chain_name, exchange)

            exchange.withdraw('ETH', self.amount, self.receiver_address, params={
                'toAddress': self.receiver_address,
                'chainName': chain_name,
                'dest': 4,
                'fee': fee,
                'pwd': '-',
                'amt': self.amount,
                'network': 'StarkNet'
            })

            logger.success(f'Successfully withdrawn {self.amount} ETH to Starknet for wallet {self.receiver_address}')

        except Exception as ex:
            logger.error(f'Something went wrong {ex}')
            return
