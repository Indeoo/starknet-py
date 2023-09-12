from src.utils.mappings import (
    module_handlers,
    bridge_handlers
)
from colorama import Fore

import random
from config import WALLET_TYPE

with open('config.py', 'r', encoding='utf-8-sig') as file:
    module_config = file.read()

exec(module_config)

if WALLET_TYPE.lower() == 'argent':
    with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
        private_keys = [line.strip() for line in file]
        random.shuffle(private_keys)
elif WALLET_TYPE.lower() == 'braavos':
    with open('braavos_wallets.txt', 'r', encoding='utf-8-sig') as file:
        private_keys = [line.strip() for line in file]


metamask_addresses = []
metamask_private_keys = []
argentx_addresses = []
argentx_private_keys = []

with open('bridge_assets/assets/metamask_wallets.txt', 'r', encoding='utf-8-sig') as file:
    for line in file:
        address, private_key = line.strip().split(':')
        metamask_addresses.append(address)
        metamask_private_keys.append(private_key)

with open('bridge_assets/assets/argentx_wallets.txt', 'r', encoding='utf-8-sig') as file:
    for line in file:
        address, private_key = line.strip().split(':')
        argentx_addresses.append(address)
        argentx_private_keys.append(private_key)

with open('okx_data/receiver_wallets.txt', 'r', encoding='utf-8-sig') as file:
    receiver_wallets = [line.strip() for line in file]

patterns = {}
bridge_patterns = {}

for module in module_handlers:
    if globals().get(module):
        patterns[module] = 'On'
    else:
        patterns[module] = 'Off'

for bridge_module in bridge_handlers:
    if globals().get(bridge_module):
        bridge_patterns[bridge_module] = 'On'
    else:
        bridge_patterns[bridge_module] = 'Off'

print(Fore.BLUE + f'Loaded {len(private_keys)} wallets')

print(f'----------------------------------------Modules--------------------------------------------')

for pattern, value in patterns.items():
    if value == 'Off':
        print("\033[31m {}".format(f'{pattern} = {value}'))
    else:
        print("\033[32m {}".format(f'{pattern} = {value}'))
print('\033[39m')

print('Created by | https://t.me/cryptoscripts')
print('Donations (Any EVM) | 0x763cDEa4a54991Cd85bFAd1FD47E9c175f53090B')
active_module = [module for module, value in patterns.items() if value == 'On']

active_bridge_modules = [bridge_module for bridge_module, value in bridge_patterns.items() if value == 'On']
