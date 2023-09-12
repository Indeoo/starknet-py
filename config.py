RANDOMIZE = True
RUN_FOREVER = False
SLIPPAGE = 0.02
ESTIMATED_FEE_MULTIPLIER = 1
NUM_THREADS = 1
MIN_PAUSE = 1200
MAX_PAUSE = 1800
MAX_FEE_FOR_TRANSACTION = 0.00053  # ETH
RPC_URL = 'https://starknet-mainnet.public.blastapi.io'
WALLET_TYPE = 'argent'  # argent/braavos
# -------------------------------------Modules--------------------------------#

# --- Deploy --- #
deploy_contracts = False

# --- Withdrawals --- #
okx_withdraw = False

# --- Bridges --- #
main_bridge = False
orbiter_bridging = False

# --- Swaps --- #

jediswap_swap = False
myswap_swap = False
k10_swap = False
sith_swap = False
anvu_swap = False
fibrous_swap = False

# --- Liquidity --- #

jedi_liq = False
jedi_liq_remove = False

myswap_liq = False
myswap_liq_remove = False

sith_liq = False
sith_liq_remove = False

k10_liq = False
k10_liq_remove = False

zklend_liq = True
zklend_liq_remove = False


# --- NFT --- #
unframed_mint = False


class OkxWithdrawConfig:
    amount_from = 0.005
    amount_to = 0.005


class MainBridgeConfig:
    amount_from = 0.037
    amount_to = 0.0415
    action = 'deposit'


class OrbiterBridgeConfig:
    chain = 'OP'  # ARB
    amount_from = 0.03  # ETH
    amount_to = 0.03
    action = 'deposit'  # withdraw/deposit
    bridge_all_balance = False


# class JediSwapConfig:
#     from_token = 'USDC'
#     to_token = 'ETH'
#     amount_from = 1.5
#     amount_to = 1.8
#     swap_all_balance = False


class MySwapConfig:
     from_token = 'ETH'
     to_token = 'USDC'
     amount_from = 0.001
     amount_to = 0.003
     swap_all_balance = False


class K10SwapConfig:
    from_token = 'ETH'
    to_token = 'USDC'
    amount_from = 0.0001
    amount_to = 0.001
    swap_all_balance = False


class SithSwapConfig:
     from_token = 'ETH'
     to_token = 'USDC'
     amount_from = 0.001
     amount_to = 0.002
     swap_all_balance = False


class AnvuSwapConfig:
     from_token = 'ETH'
     to_token = 'USDC'
     amount_from = 0.001
     amount_to = 0.002
     swap_all_balance = False


class FibrousSwapConfig:
     from_token = 'ETH'
     to_token = 'USDC'
     amount_from = 0.001
     amount_to = 0.011
     swap_all_balance = False


# class JediLiqConfig:
#     token = 'ETH'  # ETH only
#     token2 = 'USDT'  # USDT/USDC
#     amount_from = 0.0005
#     amount_to = 0.001

class JediSwapConfig:
     from_token = 'ETH'
     to_token = 'USDC'
     amount_from = 0.0001
     amount_to = 0.001
     swap_all_balance = False


# class MySwapConfig:
#     from_token = 'ETH'
#     to_token = 'USDC'
#     amount_from = 0.0005
#     amount_to = 0.0007
#     swap_all_balance = False


# class K10SwapConfig:
#     from_token = 'ETH'
#     to_token = 'USDC'
#     amount_from = 0.0005
#     amount_to = 0.001
#     swap_all_balance = False


# class SithSwapConfig:
#     from_token = 'ETH'
#     to_token = 'USDT'
#     amount_from = 0.0005
#     amount_to = 0.001
#     swap_all_balance = False


# class AnvuSwapConfig:
#     from_token = 'ETH'
#     to_token = 'DAI'
#     amount_from = 0.0005
#     amount_to = 0.001
#     swap_all_balance = False


# class FibrousSwapConfig:
#     from_token = 'ETH'
#     to_token = 'USDT'
#     amount_from = 0.0005
#     amount_to = 0.001
#     swap_all_balance = False


# class JediLiqConfig:
    # token = 'ETH'  # ETH only
    # token2 = 'USDT'  # USDT/USDC
    # amount_from = 0.0005
    # amount_to = 0.001


class JediLiqRemoveConfig:
    from_token_pair = 'USDT'  # ETH/from_token_pair
    remove_all = False
    removing_percentage = 0.5


class MySwapLiqConfig:
    token = 'ETH'  # ETH only
    token2 = 'USDC'  # USDT/USDC
    amount_from = 0.001
    amount_to = 0.001


class MySwapLiqRemoveConfig:
    from_token_pair = 'USDC'  # ETH/from_token_pair
    remove_all = False
    removing_percentage = 0.5


class SithLiqConfig:
    token = 'ETH'  # ETH only
    token2 = 'USDT'  # USDT/USDC
    amount_from = 0.001
    amount_to = 0.001


class SithLiqRemoveConfig:
    from_token_pair = 'USDT'  # ETH/from_token_pair
    remove_all = False
    removing_percentage = 0.5


class K10LiqConfig:
    token = 'ETH'  # ETH only
    token2 = 'USDC'  # USDT/USDC
    amount_from = 0.001
    amount_to = 0.001


class K10LiqRemoveConfig:
    from_token_pair = 'USDC'  # ETH/from_token_pair
    remove_all = False
    removing_percentage = 0.5


class ZKLendLiqConfig:
    token = 'ETH'  # USDC
    amount_interval = 'all_balance'
    #amount_interval = {'from': 0.0001, 'to': 0.0003}
    min_amount_interval = {'from': 0.0025, 'to': 0.0025} # for all_balance


class ZKLendLiqRemoveConfig:
    from_token_pair = 'USDT'  # ETH/from_token_pair
    remove_all = True
    removing_percentage = 0.5


class UnframedMintConfig:
    max_nft_price = 0.001  # ETH
