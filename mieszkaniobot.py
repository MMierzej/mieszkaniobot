import asyncio
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
import json
from math import ceil, floor
import os
import traceback

import bs4
from dotenv import load_dotenv
import requests
import telegram


async def send_messages(texts: Sequence[str], chat_ids: Iterable[int | str]) -> None:
    async with telegram.Bot(BOT_TOKEN) as bot:
        print(f"Sending {len(texts)} messages...")
        for chat_id in chat_ids:
            for text in texts:
                await bot.send_message(text=text, chat_id=chat_id)
                await asyncio.sleep(0.4)  # we've got throttling at home
        # # TODO: check if the below works
        # await asyncio.gather(*[asyncio.create_task(bot.send_message(text=text, chat_id=chat_id))
        #                       for chat_id in chat_ids for text in texts])
        print("Messaging done")


async def get_new_olx_offers(source: str) -> list[str]:
    """
    Returns a list of infos about new offers on OLX.
    """

    # https://www.youtube.com/watch?v=xfZZxyaW7q4&t=86s
    dawaj_zupkee = bs4.BeautifulSoup(requests.get(source).text, "html.parser")
    urls = []

    # assuming that `bs4` always parses and finds in the same way,
    # by the order of appearance from the top of the HTML.
    # without 3 first offers, which are promoted
    for post in dawaj_zupkee.find_all(class_="css-rc5s2u")[3:]:  # <a> tags
        url = "https://olx.pl" + href if (href := post["href"]).startswith("/d") else href
        if url not in VISITED:
            urls.append(url)

    VISITED.update(urls)
    with open("visited.txt", "a") as visited_txt:
        visited_txt.writelines(urls)

    return urls


with open("visited.txt", "r") as visited_txt:
    VISITED = set(map(str.strip, visited_txt))

INTERVAL_IN_MINS = 0.5
INTERVAL = ceil(INTERVAL_IN_MINS * 60) - 2
MAX_BATCH_SIZE = floor(20 * min(INTERVAL_IN_MINS, 1))


async def main():
    messages = []
    try:
        i = 0
        while (i := i + 1):
            print(i, datetime.now(timezone.utc).isoformat())

            tasks = [asyncio.create_task(get_new_olx_offers(source)) for source in SOURCES]
            messages.extend([url for task in asyncio.as_completed(tasks) for url in await task])
            msgs = messages[:MAX_BATCH_SIZE]
            if msgs:
                await send_messages(msgs, CHAT_IDS)
                messages = messages[MAX_BATCH_SIZE:]
                print(f"There are {len(messages)} messages left in the queue")

            print(i, "\n")
            await asyncio.sleep(INTERVAL)
    except:
        traceback.print_exc()
        async with telegram.Bot(BOT_TOKEN) as bot:
            await bot.send_message(text="ERROR!", chat_id=LOG_CHAT_ID)


if __name__ == "__main__":
    load_dotenv()

    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_IDS = json.loads(os.environ["CHAT_IDS"])
    LOG_CHAT_ID = os.environ["LOG_CHAT_ID"]
    SOURCES = json.loads(os.environ["SOURCES"])

    asyncio.run(main())
