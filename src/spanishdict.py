import asyncio
from typing import Optional, TypedDict
import bs4
import json
import logging
import pprint
import re
import sys

from enum import Enum, auto

import aiohttp
from html_to_markdown import convert_to_markdown
from tqdm.asyncio import tqdm

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.Logger(__name__)


NUMBER_START = r"\d+\\\."
LETTER_START = r"[a-z]+\."


class State(Enum):
    Word = auto()
    Sense = auto()
    Specific = auto()
    Done = auto()


Pair = TypedDict("Pair", {"english": str, "spanish": str})
Examples = TypedDict("Examples", {"spanish": list[str], "english": list[str]})


async def spanish_examples(session, word, count=5) -> Examples:
    url = "https://examples1.spanishdict.com/explore"
    params = {"lang": "es", "q": word, "numExplorationSentences": 100}
    result: Examples = {"spanish": [], "english": []}

    try:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            lst = [
                i for i in data["data"]["sentences"] if i["corpus"] == "open-subtitles"
            ][0:count]
            result["spanish"] = [i["source"] for i in lst]
            result["english"] = [i["target"] for i in lst]

    except Exception as e:
        logger.error(e, exc_info=True)
    return result


def spanish_dict_line_parser(input_: list[str]) -> list[tuple[State, str]]:
    def advance(prev: State, s: Optional[str]) -> State:
        if not s:
            return State.Done
        st = s.strip()

        if prev == State.Word:
            if re.search(NUMBER_START, st):
                return State.Sense
            if re.search(LETTER_START, st):
                raise Exception(f"Invalid position {prev} {s}")
            else:
                return prev
        elif prev == State.Sense:
            if re.search(NUMBER_START, st):
                return State.Sense
            elif re.search(LETTER_START, st):
                return State.Specific
            else:
                return prev
        elif prev == State.Specific:
            if re.search(NUMBER_START, st):
                return State.Sense
            elif re.search(LETTER_START, st):
                return State.Specific
            else:
                return prev

    acc = []
    prev = State.Word
    input_.reverse()
    ls: list[Optional[str]] = [None] + input_
    curr = ""

    while ls:
        s = ls.pop()
        nxt = advance(prev, s)
        # print(prev, nxt, s)
        if s:
            if prev == nxt:
                acc.append((prev, curr))
                curr = s
            else:
                acc.append((prev, curr))
                curr = s
        else:
            acc.append((prev, curr))
        prev = nxt

    result = []
    for state, s in acc:
        match state:
            case State.Word:
                pass
                # result.append(f"<strong>{s}</strong>")
            case State.Sense:
                result.append(" " + s.replace("\\", ""))
            case State.Specific:
                result.append("     " + s)
            case State.Done:
                result.append(s)
    return result


def spanish_dict_parsing(soup: bs4.BeautifulSoup) -> str:
    if not soup:
        raise Exception("Failed to find: {}")

    # Delete all tags I don't want
    for tag_name in ["button", "img", "video", "audio", "source", "picture", "iframe"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Replace links with inner text
    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        if href.startswith("https://www.spanishdict.com") and "translate" not in href:
            a_tag.decompose()
        else:
            a_tag.replace_with(a_tag.get_text())

    pronounciation = soup.find("span", id="dictionary-link-es")
    pronounciation.decompose()

    for span_tag in soup.find_all("span"):
        # get rid of useless info spans
        if span_tag.get("lang") in {"es", "en"}:
            span_tag.decompose()
        else:
            # spans have too much nesting, I just want the text
            span_tag.replace_with(span_tag.get_text())

    # Get rid of really basic stuff like what a masculine noun is
    for div_tag in soup.find_all("div"):
        if div_tag.attrs:
            div_style = div_tag.get("style")
            if div_style:
                div_style = div_style.replace(" ", "")
                if div_style == "width:220px":
                    div_tag.decompose()
        # # My stuff has created some linebreaks in my divs
        # else:
        #     div_tag.string = div_tag.get_text(separator='', strip=True)

    markdown = convert_to_markdown(soup).replace(".", ". ")
    lines = [i for i in markdown.split("\n") if i]
    parsed = spanish_dict_line_parser(lines)
    return parsed


async def spanish_dict_request(session, word):
    url = f"https://www.spanishdict.com/translate/{word}"
    es_div = None
    try:
        async with session.get(url) as resp:
            text = await resp.text()
            soup = bs4.BeautifulSoup(text, "html.parser")
            es_div = soup.find("div", id="dictionary-neodict-es")
    except Exception as e:
        logger.error(e, exc_info=True)

    if not es_div:
        pprint.pprint(soup)
        raise Exception(f"{word} not found")
    return es_div


async def spanish_word(session, word) -> Pair:
    soup = await spanish_dict_request(session, word)
    if soup:
        parsed = spanish_dict_parsing(soup)
    else:
        raise Exception(f"Word not found: {word}")

    examples = await spanish_examples(session, word, count=2)
    english = f"""<pre>{"<br>".join(parsed)}<br></pre>{"<br>".join([f"<i>{i}</i>" for i in examples["english"]])}"""
    spanish = f"""<pre><strong>{word}</strong><br></pre>{"<br>".join(f"<i>{i}</i>" for i in examples["spanish"])}"""
    return {"spanish": spanish, "english": english}


async def process_file(input_file: str, output_file: str):
    async with aiohttp.ClientSession() as sesh:
        with open(input_file, "r") as f:
            lines = [i.strip() for i in f.readlines()]

        successes, failures = [], []
        results = []
        async for word in tqdm(lines):
            try:
                result = await spanish_word(sesh, word)
                results.append(result)
                successes.append(word)
            except Exception as e:
                logger.error(e)
                failures.append(word)

        with open(output_file, "w") as f:
            all_lines = "\n".join([i["english"] + "\t" + i["spanish"] for i in results])
            f.write(all_lines)

        print("SUCCESSES")
        pprint.pprint(successes)
        print("FAILURES")
        pprint.pprint(failures)
        # # ex = await spanish_word(sesh, "atardecer")
        # pprint.pprint(ex)
