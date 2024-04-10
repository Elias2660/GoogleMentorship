import requests
from openai import OpenAI
import tiktoken
import dotenv
import asyncio
import pandas as pd
import numpy as np
from pyppeteer import launch

# ? getting the api keys

GOOGLE_API = dotenv.get_key("../.env", "GOOGLE_SEARCH_API")
GPT_API = dotenv.get_key("../.env", "GPT_API")
SEARCH_ENGINE_ID = dotenv.get_key("../.env", "SEARCH_ENGINE_ID")

NUMBER = 5 # for testing purposes :3

model = "gpt-4-turbo-preview"
context = 128000
max_out = 4096


if __name__ == "__main__":
    """
    if NUMBER is -1, then run for all elements in the dataset
    else if then run the thing for the number of viruses that exist
    """
    data = pd.DataFrame(columns =["Virus Name", "R0 Value", "Range of R0 Values", "Source1" "Source 2"])
    
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


def summarize(
    text: str,
    token_limit=context,
    goal="finding r0 values in relation to diseases",
    model=model,
) -> str:
    """
    Given a lot of text, summarize it

    If there are too many tokens, then split it until there are enough tokens that can be splitable
    """
    system_message = """
        The job of you as a model is to summarize text; while retaining as much important information as possible
        Important information includes specific numbers and numerals.
    """

    command = f"""
        Please summarize the following text into 7 or less sentences, paying special attention to the {goal}.
        Keep numbers related to {goal} accurate, and them within the context that was in the webpage.
        
        Here's the text to summarize:
        {text}
    """
    tokens = get_number_of_tokens(command + system_message)
    if tokens > token_limit:
        # summarize both sides of the text
        return (
            summarize(text[0 : int(text.length) - 1])
            + "\n"
            + summarize(text[int(text.length - 1)])
        )

    client = OpenAI(api_key=GPT_API)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": command},
        ],
    )

    return completion.choices[0].message.content

    # use the extracted data to plug into the gpt


def get_result(summarized_data: str, virus: str) -> np.ndarray:
    """
    given the summarized context, return a string containing the result
    """
    client = OpenAI(api_key=GPT_API)
    system_message = f"""
    Write as an output no more words than specified. 
    
    In total, there should be at most four lines out.
    
    The first one should have two numbers, separated with a comma, the next should have a citation, and the next should either be blank or have a citation, as a URL.
    
    If you provide an url providing information on the r naught value of the virus {virus}, please make sure it is a reliable source and included the r0 value of {virus} in the text.
    
    Here's some information: 
    {summarized_data}
    """
    command = f"""
    Write as an output no more words than specified. In total, there should be at most four lines out. The first one should have two numbers, separated with a comma, the next should have a citation, and the next should either be blank or have a citation, preferably as a URL.
    
    Write the average R0 value of {virus} in the first line. Do it in numeric form to the 2nd decimal. If the R0 values do not exist, estimate one value from the range given and put the range after that value with a comma separating them. This should be one line. If you cannot find a range, print “NaN”
    
    In the following two lines, put the sources, preferably as URLs, that helped lead you to this conclusion, after that end the response. If you only have one source, please put it on the first line, leaving the second one blank.
    
    Double-check your result. In the following line, output either “true” if both the citations relate to the average R0 value of the virus {virus}. If not, output “false”. 
    
    Write as an output no more words than specified. In total, there should be at most four lines out. The first one should have two numbers separated with a comma, the next should have a some form of citation, and the next should either be blank or have some form of citation. The final should have a true/false value based upon if you found the sources to be actually related when double checking your work.
    """
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": command},
        ],
    )
    array_return = np.full(shape=5, fill_value=np.nan)
    elements = np.split("\n")
    array_return[0] = virus
    array_return[1], array_return[2] = elements[0].split(",")
    array_return[3] = elements[1]
    array_return[4] = elements[2] if elements[2] == "" else np.nan
    
    return array_return
