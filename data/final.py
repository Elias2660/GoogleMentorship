# %%

import dotenv
import asyncio
import utils
import numpy as np
import csv


# %%
# ? getting the api keys

GOOGLE_API = dotenv.get_key("../.env", "GOOGLE_SEARCH_API")
GPT_API = dotenv.get_key("../.env", "GPT_API")
SEARCH_ENGINE_ID = dotenv.get_key("../.env", "SEARCH_ENGINE_ID")

NUMBER = 5  # for testing purposes :3

MODEL = "gpt-4-turbo-preview"
CONTEXT = 128000
MAX_OUT = 4096

output = {}


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def getGPTAnswer(virus: str) -> str:

    Query = f"What is the R0 value of {virus}"

    print(f"{bcolors.OKCYAN} GETTING DATA {bcolors.ENDC}")
    data = utils.get_data(Query)
    print(f"{bcolors.OKGREEN} DATA FOUND {bcolors.ENDC}")

    summaried = ""
    for link in data:

        print(f"{bcolors.OKCYAN} GETTING DATA FROM LINK:{bcolors.ENDC} {link} ")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        text = ""
        try:
            text = loop.run_until_complete(utils.get_text(link))
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        print(f"{bcolors.OKGREEN} GOTTEN TEXT {bcolors.ENDC}")

        print(f"{bcolors.OKCYAN} SUMMARIZING TEXT {bcolors.ENDC}")
        summarized_text = f"Source: {link} \n {utils.summarize(text)}"
        print(f"{bcolors.OKGREEN} SUMMARIZED {bcolors.ENDC}")

        print(summarized_text)

        print(f"{bcolors.OKCYAN} CHECKING FOR LENGTH {bcolors.ENDC}")
        if (
            utils.get_tokens_for_result(summaried, virus=virus)
            + utils.get_number_of_tokens(summarized_text)
            < CONTEXT
        ):
            print(f"{bcolors.OKGREEN} LENGTH CHECKED {bcolors.ENDC}")
            summaried += f"\n {summarized_text}"
        else:
            break
    print(f"{bcolors.OKCYAN} PRINTING RESULT {bcolors.ENDC}")
    final = utils.get_result(summaried, virus=virus)
    print(final)
    print(f"{bcolors.OKGREEN} RESULT PRINTED {bcolors.ENDC}")
    if final is None:
        return """NaN
    
    
    false"""
    else:
        return final

# %%


def switch_to_csv(ans: str, virus: str) -> list:
    lines = ans.split("\n")
    numbers = [virus]
    for index in range(len(lines) - 1):
        if index == 0 and lines[0].strip() != "NaN":
            words = lines[index].split(",")
            print(words)
            numbers.append(words[0].strip())
            numbers.append(words[1].strip())
        elif index == 0:
            numbers.append("NaN")
            numbers.append(" ")
        else:
            if lines[index] == "" and len(lines) <= 2:
                numbers.append(lines[index])
            elif lines[index] != "":
                numbers.append(lines[index])
    return numbers


def main():
    try:
        with open("Virus List.txt", "r") as virusList, open("output.csv", "w") as f:
            w = csv.writer(f)
            for line in virusList:
                virus = line.strip()  # remove newline characters
                print(f"ADDING VIRUS {virus}")
                ans = switch_to_csv(getGPTAnswer(virus), virus)
                print(ans)
                w.writerow(
                    ans
                )  # assuming this function is defined elsewhere
                print(f"ADDED VIRUS")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
