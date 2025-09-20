import asyncio
import bs4
import json
import logging
import pprint

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.Logger(__name__)


async def spanish_examples(session, word, count=5) -> list[str]:
    url = "https://examples1.spanishdict.com/explore"
    params = {"lang": "es", "q": word, "numExplorationSentences": 100}
    try:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            logger.info(data)
            return data["data"]["sentences"][0:count]
    except Exception as e:
        logger.error(e, exc_info=True)
    return []


def spanish_dict_parsing(soup: bs4.BeautifulSoup) -> str:
    mydiv = soup.find("div", id="dictionary-neodict-es")

    # Delete all tags I don't want
    for tag_name in ["button", "img", "video", "audio", "source", "picture", "iframe"]:
        for tag in mydiv.find_all(tag_name):
            tag.decompose()

    # Replace links with inner text
    for a_tag in mydiv.find_all("a"):
        a_tag.replace_with(a_tag.get_text())

    return mydiv


async def spanish_word(session, word):
    url = f"https://www.spanishdict.com/translate/{word}"
    try:
        async with session.get(url) as resp:
            text = await resp.text()
            logger.info(text)
            soup = bs4.BeautifulSoup(text, "html.parser")
            logger.info(soup)
            return soup
    except Exception as e:
        logger.error(e, exc_info=True)


async def main():
    async with aiohttp.ClientSession() as sesh:
        "html body.no-touch.vsc-initialized div#root div.Spcmr8DS div.WuDqSfpG div#main-container-flex.i93qwEyU div#main-container-video.Y6PXtKDi.GsRSuzwj"
        # ex = await spanish_examples(sesh, "atardecer")
        ex = await spanish_word(sesh, "atardecer")
        pprint.pprint(ex)


if __name__ == "__main__":
    asyncio.run(main())
