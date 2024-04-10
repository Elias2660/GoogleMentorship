import requests
from openai import OpenAI
import tiktoken
import dotenv
import asyncio
from pyppeteer import launch

# ? getting the api keys

GOOGLE_API = dotenv.get_key("../.env", "GOOGLE_SEARCH_API")
GPT_API = dotenv.get_key("../.env", "GPT_API")
SEARCH_ENGINE_ID = dotenv.get_key("../.env", "SEARCH_ENGINE_ID")

NUMBER = 5

model = "gpt-4-turbo-preview"
context = 128000
max_out = 4096


if __name__ == "__main__":
    """
    if NUMBER is -1, then run for all elements in the dataset
    else if then run the thing for the number of viruses that exist
    """
    print("hello world")

# the data gathering steps


# use  google search api to get  a list different search results


def get_data(
    Query: str, Google_API_KEY=GOOGLE_API, Search_Engine_ID=SEARCH_ENGINE_ID
) -> list:
    final = []
    URL = f"https://www.googleapis.com/customsearch/v1?key={Google_API_KEY}&cx={Search_Engine_ID}&q={Query}"
    response = requests.get(
        f"https://www.googleapis.com/customsearch/v1?key={Google_API_KEY}&cx={Search_Engine_ID}&q={Query}"
    )
    for item in response.json()["items"]:
        final.append(item["link"])
    return final


# for every search result, use pyppeteer to extract the textual data


async def get_text(URL: str) -> str:
    browser = await launch()
    page = await browser.newPage()
    await page.goto(URL)
    content = await page.evaluate('() => document.querySelector("*").innerText')
    await browser.close()
    return content


def get_encodings(text: str, model="gpt-4") -> list:
    encoding = tiktoken.encoding_for_model(model)
    return encoding.encode(text)


def get_number_of_tokens(text: str, model="gpt-4") -> list:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


# the summarize the textual data, saving as many numbers of as possible


def summarize(text: str, token_limit = context) -> str:
    """
    Given a lot of text, summarize it

    If there are too many tokens, then split it until there are enough tokens that can be splitable
    """
    system_message = """
        The job of you as a model is to summarize text; while retaining as much important information as possible
        Important information includes specific numbers and numerals.
    """

    command = """"""
    tokens = get_number_of_tokens(text + command + system_message)
    while (tokens > token_limit):
        # cut the tokens down to half
        ...
    
    client = OpenAI(api_key=GPT_API)

    return ""

    # use the extracted data to plug into the gpt


def getResult(summarized_data: str) -> str: ...


# %%
