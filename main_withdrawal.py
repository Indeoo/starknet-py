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

from src.utils.mappings import module_handlers
from src.utils.helper import (
    receiver_wallets,
)

from okx_data.okx_data import (
    API_KEY,
    SECRET_KEY,
    PASSPHRASE,
)

from src.utils.runner import process_okx_withdrawal


async def main() -> bool:
    tasks = []
    for receiver_wallet in receiver_wallets:
        task = create_task(process_okx_withdrawal(API_KEY, SECRET_KEY, PASSPHRASE, receiver_wallet))
        tasks.append(task)
        time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
        logger.info(f'Sleeping {time_to_sleep} seconds...')
        await sleep(time_to_sleep)
        await task
    await gather(*tasks)
    return all(task.done() for task in tasks)


def start_event_loop(awaitable: Awaitable[object], loop: AbstractEventLoop) -> None:
    loop.run_until_complete(awaitable)


if __name__ == '__main__':
    with tqdm(total=len(receiver_wallets)) as pbar:
        async def tracked_main():
            await main()

        start_event_loop(tracked_main(), get_event_loop())
        pbar.close()
