from typing import Awaitable
import random
import copy

from asyncio import (
    create_task,
    gather,
    sleep,
    get_event_loop,
    Semaphore,
    AbstractEventLoop,
)

from loguru import logger
from tqdm import tqdm
from config import *

from src.utils.mappings import bridge_handlers
from src.utils.helper import (
    metamask_addresses,
    metamask_private_keys,
    argentx_addresses,
    argentx_private_keys,
    active_bridge_modules,
)


async def process_private_key(metamask_address: str,
                              metamask_private_key: str,
                              argentx_address: str,
                              argentx_private_key: str,
                              thread_num: int,
                              semaphore: Semaphore) -> bool:
    tasks = []
    if RANDOMIZE is True:
        modules = copy.copy(active_bridge_modules)
        random.shuffle(modules)
    else:
        modules = active_bridge_modules
    async with semaphore:
        for pattern in modules:
            task = create_task(bridge_handlers[pattern](
                metamask_address,
                metamask_private_key,
                argentx_address,
                argentx_private_key,
            ))
            tasks.append(task)
            time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
            logger.info(f'Thread {thread_num}: Sleeping {time_to_sleep} seconds...')
            await sleep(time_to_sleep)
            await task
        await gather(*tasks)
    return all(task.done() for task in tasks)


async def main(loop: AbstractEventLoop) -> None:
    if len(metamask_addresses) != len(argentx_addresses):
        print(len(metamask_addresses), len(argentx_addresses))
        logger.error('Number of metamask wallets does not match number of argentx wallets')
        return
    num_threads = min(NUM_THREADS, len(argentx_addresses))
    semaphore = Semaphore(num_threads)

    if not RUN_FOREVER:
        tasks = []
        thread_num = 1
        for metamask_addr, metamask_key, argentx_addr, argentx_key in zip(
                metamask_addresses,
                metamask_private_keys,
                argentx_addresses,
                argentx_private_keys,
        ):
            task = loop.create_task(process_private_key(
                metamask_addr,
                metamask_key,
                argentx_addr,
                argentx_key,
                thread_num,
                semaphore,
            ))
            tasks.append(task)
            thread_num += 1
        await gather(*tasks)

    while RUN_FOREVER:
        tasks = []
        thread_num = 1
        for metamask_addr, metamask_key, argentx_addr, argentx_key in zip(
                metamask_addresses,
                metamask_private_keys,
                argentx_addresses,
                argentx_private_keys,
        ):
            task = loop.create_task(process_private_key(
                metamask_addr,
                metamask_key,
                argentx_addr,
                argentx_key,
                thread_num,
                semaphore,
            ))
            tasks.append(task)
            thread_num += 1
        await gather(*tasks)


def start_event_loop(awaitable: Awaitable[object], loop: AbstractEventLoop) -> None:
    loop.run_until_complete(awaitable)


if __name__ == '__main__':
    with tqdm(total=len(argentx_addresses)) as pbar:
        async def tracked_main():
            await main(get_event_loop())


        start_event_loop(tracked_main(), get_event_loop())
        pbar.close()
