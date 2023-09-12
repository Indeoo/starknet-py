import random

from loguru import logger

from src.modules.swaps.anvuswap.anvuswap import AnvuSwap

from config import *

from src.modules.bridges.orbiter.utils.transaction_data import get_router
from src.modules.swaps.fibrous_swap.fibrous_swap import FibrousSwap
from src.modules.nfts.unframed.unframed_mint import UnframedMint
from src.modules.deploying.deploy_contracts import DeployContracts
from src.modules.okx_withdraw.okx_withdraw import OkxWithdraw

from src.modules.bridges.orbiter.orbiter_bridge import (
    OrbiterBridgeDeposit,
    OrbiterBridgeWithdraw,
)

from src.modules.swaps.k10_swap.k10_swap import (
    K10LiquidityRemove,
    K10Liquidity,
    K10Swap,
)

from src.modules.swaps.sithswap.sithswap import (
    SithLiquidityRemove,
    SithSwapLiquidity,
    SithSwap,
)

from src.modules.swaps.myswap.myswap import (
    MySwapLiquidityRemove,
    MySwapLiquidity,
    MySwap,
)

from src.modules.swaps.zk_lend.zk_lend import (
    ZKLendLiquidity,
    ZKLendLiquidityRemove,
)

from src.utils.chains import (
    chain_mapping,
    STARKNET,
)

from src.modules.swaps.jediswap.jediswap import (
    JediLiquidityRemove,
    JediLiquidity,
    JediSwap,
)


async def process_okx_withdrawal(api_key: str, api_secret: str, passphrase: str, receiver_address: str):
    amount_from = OkxWithdrawConfig.amount_from
    amount_to = OkxWithdrawConfig.amount_to

    withdrawal = OkxWithdraw(api_key, api_secret, passphrase, amount_from, amount_to, receiver_address)
    logger.info('Withdrawing from OKX...')
    await withdrawal.withdraw()


async def process_orbiter_bridging(metamask_address: str,
                                   metamask_private_key: str,
                                   argentx_address: str,
                                   argentx_private_key: str,
                                   ) -> None:
    supported_chains = ['ARB']
    amount_from = OrbiterBridgeConfig.amount_from
    amount_to = OrbiterBridgeConfig.amount_to
    action = OrbiterBridgeConfig.action
    bridge_all_balance = OrbiterBridgeConfig.bridge_all_balance
    contract_router = await get_router('ETH')

    if OrbiterBridgeConfig.action.lower() == 'deposit':
        rpc_chain = chain_mapping[OrbiterBridgeConfig.chain.lower()].rpc
        code = STARKNET.code
        chain = OrbiterBridgeConfig.chain
        if chain.upper() not in supported_chains:
            logger.error(f'Not supported chain {chain}. Use only: ARB')
            return
        bridger = OrbiterBridgeDeposit(
            private_key=metamask_private_key,
            receiver_address=argentx_address,
            rpc_chain=rpc_chain,
            bridge_contract=contract_router,
            chain=chain,
            amount_from=amount_from,
            amount_to=amount_to,
            code=code)
        logger.info('Bridging on Orbiter Bridge to StarkNet...')
        await bridger.deposit()

    elif OrbiterBridgeConfig.action.lower() == 'withdraw':
        code = chain_mapping[OrbiterBridgeConfig.chain.lower()].code
        chain = OrbiterBridgeConfig.chain
        if chain not in supported_chains:
            logger.error(f'Not supported chain {chain}. Use only: ARB')
            return
        bridger = OrbiterBridgeWithdraw(
            private_key=argentx_private_key,
            chain=chain,
            receiver_address=metamask_address,
            amount_from=amount_from,
            amount_to=amount_to,
            bridge_all_balance=bridge_all_balance,
            code=code)
        logger.info(f'Bridging on Orbiter Bridge from StarkNet to {chain.upper()}...')
        await bridger.withdraw()
    else:
        logger.error('Unknown action, use only: deposit/withdraw')
        return


async def process_jediswap_swap(private_key: str) -> None:
    from_token = JediSwapConfig.from_token
    to_token = JediSwapConfig.to_token
    amount_from = JediSwapConfig.amount_from
    amount_to = JediSwapConfig.amount_to
    swap_all_balance = JediSwapConfig.swap_all_balance

    jediswap_swap = JediSwap(private_key=private_key,
                             from_token=from_token,
                             to_token=to_token,
                             amount_from=amount_from,
                             amount_to=amount_to,
                             swap_all_balance=swap_all_balance)
    logger.info('Swapping on Jediswap...')
    await jediswap_swap.swap()


async def process_myswap_swap(private_key: str) -> None:
    from_token = MySwapConfig.from_token
    to_token = MySwapConfig.to_token
    amount_from = MySwapConfig.amount_from
    amount_to = MySwapConfig.amount_to
    swap_all_balance = MySwapConfig.swap_all_balance

    myswap_swap = MySwap(private_key=private_key,
                         from_token=from_token,
                         to_token=to_token,
                         amount_from=amount_from,
                         amount_to=amount_to,
                         swap_all_balance=swap_all_balance)
    logger.info('Swapping on MySwap...')
    await myswap_swap.swap()


async def process_k10_swap(private_key: str) -> None:
    from_token = K10SwapConfig.from_token
    to_token = K10SwapConfig.to_token
    amount_from = K10SwapConfig.amount_from
    amount_to = K10SwapConfig.amount_to
    swap_all_balance = K10SwapConfig.swap_all_balance

    k10_swap = K10Swap(private_key=private_key,
                       from_token=from_token,
                       to_token=to_token,
                       amount_from=amount_from,
                       amount_to=amount_to,
                       swap_all_balance=swap_all_balance)
    logger.info('Swapping on 10kSwap...')
    await k10_swap.swap()


async def process_sith_swap(private_key: str) -> None:
    from_token = SithSwapConfig.from_token
    to_token = SithSwapConfig.to_token
    amount_from = SithSwapConfig.amount_from
    amount_to = SithSwapConfig.amount_to
    swap_all_balance = SithSwapConfig.swap_all_balance

    sith_swap = SithSwap(private_key=private_key,
                         from_token=from_token,
                         to_token=to_token,
                         amount_from=amount_from,
                         amount_to=amount_to,
                         swap_all_balance=swap_all_balance)
    logger.info('Swapping on SithSwap...')
    await sith_swap.swap()


async def process_anvu_swap(private_key: str) -> None:
    from_token = AnvuSwapConfig.from_token
    to_token = AnvuSwapConfig.to_token
    amount_from = AnvuSwapConfig.amount_from
    amount_to = AnvuSwapConfig.amount_to
    swap_all_balance = AnvuSwapConfig.swap_all_balance

    anvu_swap = AnvuSwap(private_key=private_key,
                         from_token=from_token,
                         to_token=to_token,
                         amount_from=amount_from,
                         amount_to=amount_to,
                         swap_all_balance=swap_all_balance)
    logger.info('Swapping on AnvuSwap...')
    await anvu_swap.swap()


async def process_fibrous_swap(private_key: str) -> None:
    from_token = FibrousSwapConfig.from_token
    to_token = FibrousSwapConfig.to_token
    amount_from = FibrousSwapConfig.amount_from
    amount_to = FibrousSwapConfig.amount_to
    swap_all_balance = FibrousSwapConfig.swap_all_balance

    fibrous_swap = FibrousSwap(private_key=private_key,
                               from_token=from_token,
                               to_token=to_token,
                               amount_from=amount_from,
                               amount_to=amount_to,
                               swap_all_balance=swap_all_balance)
    logger.info('Swapping on FibrousSwap...')
    await fibrous_swap.swap()


async def process_jedi_liq(private_key: str) -> None:
    token = JediLiqConfig.token
    token2 = JediLiqConfig.token2
    amount_from = JediLiqConfig.amount_from
    amount_to = JediLiqConfig.amount_to
    jedi_liq = JediLiquidity(private_key=private_key,
                             token=token,
                             token2=token2,
                             amount_from=amount_from,
                             amount_to=amount_to)
    logger.info('Adding liquidity on JediSwap...')
    await jedi_liq.add_liquidity()


async def process_jedi_liq_remove(private_key: str) -> None:
    from_token_pair = JediLiqRemoveConfig.from_token_pair
    remove_all = JediLiqRemoveConfig.remove_all
    removing_percentage = JediLiqRemoveConfig.removing_percentage
    jedi_liq_remove = JediLiquidityRemove(private_key=private_key,
                                          from_token_pair=from_token_pair,
                                          remove_all=remove_all,
                                          removing_percentage=removing_percentage)
    logger.info('Removing liquidity from JediSwap...')
    await jedi_liq_remove.remove_liquidity()


async def process_myswap_liq(private_key: str) -> None:
    token = MySwapLiqConfig.token
    token2 = MySwapLiqConfig.token2
    amount_from = MySwapLiqConfig.amount_from
    amount_to = MySwapLiqConfig.amount_to
    myswap_liq = MySwapLiquidity(private_key=private_key,
                                 token=token,
                                 token2=token2,
                                 amount_from=amount_from,
                                 amount_to=amount_to)
    logger.info('Adding liquidity on MySwap...')
    await myswap_liq.add_liquidity()


async def process_sith_liq(private_key: str) -> None:
    token = SithLiqConfig.token
    token2 = SithLiqConfig.token2
    amount_from = SithLiqConfig.amount_from
    amount_to = SithLiqConfig.amount_to
    sith_liq = SithSwapLiquidity(private_key=private_key,
                                 token=token,
                                 token2=token2,
                                 amount_from=amount_from,
                                 amount_to=amount_to)
    logger.info('Adding liquidity on SithSwap...')
    await sith_liq.add_liquidity()


async def process_sith_liq_remove(private_key: str) -> None:
    from_token_pair = SithLiqRemoveConfig.from_token_pair
    remove_all = SithLiqRemoveConfig.remove_all
    removing_percentage = SithLiqRemoveConfig.removing_percentage
    sith_liq_remove = SithLiquidityRemove(private_key=private_key,
                                          from_token_pair=from_token_pair,
                                          remove_all=remove_all,
                                          removing_percentage=removing_percentage)
    logger.info('Removing liquidity from SithSwap...')
    await sith_liq_remove.remove_liquidity()


async def process_myswap_liq_remove(private_key: str) -> None:
    from_token_pair = MySwapLiqRemoveConfig.from_token_pair
    remove_all = MySwapLiqRemoveConfig.remove_all
    removing_percentage = MySwapLiqRemoveConfig.removing_percentage
    myswap_liq_remove = MySwapLiquidityRemove(private_key=private_key,
                                              from_token_pair=from_token_pair,
                                              remove_all=remove_all,
                                              removing_percentage=removing_percentage)
    logger.info('Removing liquidity from MySwap...')
    await myswap_liq_remove.remove_liquidity()


async def process_k10_liq(private_key: str) -> None:
    token = K10LiqConfig.token
    token2 = K10LiqConfig.token2
    amount_from = K10LiqConfig.amount_from
    amount_to = K10LiqConfig.amount_to
    k10_liq = K10Liquidity(private_key=private_key,
                           token=token,
                           token2=token2,
                           amount_from=amount_from,
                           amount_to=amount_to)
    logger.info('Adding liquidity on 10k Swap...')
    await k10_liq.add_liquidity()


async def process_k10_liq_remove(private_key: str) -> None:
    from_token_pair = K10LiqRemoveConfig.from_token_pair
    remove_all = K10LiqRemoveConfig.remove_all
    removing_percentage = K10LiqRemoveConfig.removing_percentage
    k10_liq_remove = K10LiquidityRemove(private_key=private_key,
                                        from_token_pair=from_token_pair,
                                        remove_all=remove_all,
                                        removing_percentage=removing_percentage)
    logger.info('Removing liquidity from 10k Swap...')
    await k10_liq_remove.remove_liquidity()


async def process_zklend_liq(private_key: str) -> None:
    token = ZKLendLiqConfig.token
    zklend_liq = ZKLendLiquidity()
    await zklend_liq.initialize(
        private_key=private_key,
        token=token,
        amount_interval=ZKLendLiqConfig.amount_interval,
        min_amount_interval=ZKLendLiqConfig.min_amount_interval
    )
    logger.info('Adding liquidity on ZkLend...')
    await zklend_liq.add_liquidity()


async def process_zklend_liq_remove(private_key: str) -> None:
    from_token_pair = ZKLendLiqRemoveConfig.from_token_pair
    remove_all = ZKLendLiqRemoveConfig.remove_all
    removing_percentage = ZKLendLiqRemoveConfig.removing_percentage
    zklend_liq_remove = ZKLendLiquidityRemove(private_key=private_key,
                                              token=from_token_pair,
                                              remove_all=remove_all,
                                              removing_percentage=removing_percentage)
    logger.info('Removing liquidity from ZkLend...')
    await zklend_liq_remove.remove_liquidity()


async def process_unframed_nft_mint(private_key: str) -> None:
    max_nft_price = UnframedMintConfig.max_nft_price

    unframed_mint = UnframedMint(private_key=private_key,
                                 max_nft_price=max_nft_price)

    logger.info('Minting NFT on Unframed...')
    await unframed_mint.mint()


async def process_deploy_contracts(private_key: str) -> None:
    deployer = DeployContracts(private_key=private_key)
    logger.info('Deploying contracts...')
    await deployer.deploy_contract()
