from src.utils.runner import *

module_handlers = {
    'jediswap_swap': process_jediswap_swap,
    'myswap_swap': process_myswap_swap,
    'k10_swap': process_k10_swap,
    'sith_swap': process_sith_swap,
    'anvu_swap': process_anvu_swap,
    'fibrous_swap': process_fibrous_swap,
    'jedi_liq': process_jedi_liq,
    'jedi_liq_remove': process_jedi_liq_remove,
    'myswap_liq': process_myswap_liq,
    'myswap_liq_remove': process_myswap_liq_remove,
    'sith_liq': process_sith_liq,
    'sith_liq_remove': process_sith_liq_remove,
    # 'main_bridge': process_main_bridge,
    'k10_liq': process_k10_liq,
    'k10_liq_remove': process_k10_liq_remove,
    'zklend_liq': process_zklend_liq,
    'zklend_liq_remove': process_zklend_liq_remove,
    'unframed_mint': process_unframed_nft_mint,
    'deploy_contracts': process_deploy_contracts
}

bridge_handlers = {
    'orbiter_bridging': process_orbiter_bridging,
}
