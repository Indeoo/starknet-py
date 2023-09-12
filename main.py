from typing import Awaitable
import random

from asyncio import (
    create_task,
    gather,
    sleep,
    run
)

from loguru import logger
from tqdm import tqdm
from config import *

from src.utils.mappings import module_handlers
from src.utils.helper import (
    private_keys,
    active_module,
)


async def main() -> None:
    tasks = []
    if RUN_FOREVER:
        while True:
            for private_key in private_keys:
                if RANDOMIZE is False:
                    for pattern in active_module:
                        try:
                            task = create_task(module_handlers[pattern](private_key))
                            tasks.append(task)
                            time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
                            logger.info(f'Sleeping {time_to_sleep} seconds...')
                            await task
                            await sleep(time_to_sleep)
                        except Exception as ex:
                            logger.error(f'Something went wrong {ex}')
                            continue

                else:
                    try:
                        random_index = random.randint(0, len(active_module) - 1)
                        random_element = active_module[random_index]
                        task = create_task(module_handlers[random_element](private_key))
                        tasks.append(task)
                        time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
                        logger.info(f'Sleeping {time_to_sleep} seconds...')
                        await task
                        await sleep(time_to_sleep)
                    except Exception as ex:
                        logger.error(f'Something went wrong {ex}')
                        pass

    else:
        for private_key in private_keys:
            if RANDOMIZE is False:
                for pattern in active_module:
                    try:
                        task = create_task(module_handlers[pattern](private_key))
                        tasks.append(task)
                        time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
                        logger.info(f'Sleeping {time_to_sleep} seconds...')
                        await task
                        await sleep(time_to_sleep)
                    except Exception as ex:
                        logger.error(f'Something went wrong {ex}')
                        continue

            else:
                random.shuffle(active_module)
                for pattern in active_module:
                    try:
                        task = create_task(module_handlers[pattern](private_key))
                        tasks.append(task)
                        time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
                        logger.info(f'Sleeping {time_to_sleep} seconds...')
                        await task
                        await sleep(time_to_sleep)
                    except Exception as ex:
                        logger.error(f'Something went wrong {ex}')
                        continue

    await gather(*tasks)


def start_event_loop(awaitable: Awaitable[object]) -> None:
    run(awaitable)


if __name__ == '__main__':
    with tqdm(total=len(private_keys)) as pbar:
        async def tracked_main():
            await main()


        start_event_loop(tracked_main())
