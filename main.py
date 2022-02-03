import requests
import asyncio
import json
import pprint
import time

# generate random integer values
from random import seed
from random import randint

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

# soup = BeautifulSoup(html_doc, 'html.parser')

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

START_TIME = default_timer()
seed(1)

def request(session, url, identifyingVal):
    # URL for API request to obtain the metadata based upon a study.
    # url = 'https://www.ebi.ac.uk/ols/api/terms?page=' + str(pageNum) + '&size=1000'
    with session.get(url) as response:
        data = response.text

        if response.status_code != 200:
            print("FAILURE::{0}".format(url))
            data = ""

        elapsed_time = default_timer() - START_TIME
        completed_at = "{:5.2f}s".format(elapsed_time)
        print("{0:<30} {1:>20}".format(identifyingVal, completed_at))
        return data

# Page numbers 0 - 7148. Size will be max of 1000; will probably make it be 1000 every time.
def getPaginatedTermsJson(session, pageNum):
    url = 'https://www.ebi.ac.uk/ols/api/terms?page=' + str(pageNum) + '&size=1000'
    randVal = randint(0, 100)
    time.sleep(randVal)
    data = request(session, url, pageNum)
    if(data == ""):
        data = getPaginatedTermsJson(session, pageNum)
    return data

async def start_async_process():
    results = []
    jsTreeUrlsArray = []
    childrenUrlsArray = []
    # pagesArray = [0, 1, 2]
    pagesArray = list(range(0, 4))
    # pagesArray = list(range(0, 7156))
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:

            # asynchronously make an api call for each study
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    getPaginatedTermsJson,
                    *(session, i)
                )
                for i in pagesArray
            ]

            # Run once everything is complete.
            for response in await asyncio.gather(*tasks):
                inputJson = response
                buildTermApiUrlsArrays(inputJson, jsTreeUrlsArray, childrenUrlsArray)
                pass

            print("jsTreeUrlsArray")
            print(len(jsTreeUrlsArray))
            print("childrenUrlsArray")
            print(len(childrenUrlsArray))


def writeAllJsTree(term):
    # TODO
    return None

def writeTextToFile(outputFileName, text):
    # TODO
    with open(outputFileName, 'w') as f:
        f.write(text)
    return None


def buildTermApiUrlsArrays(inputJson, jsTreeUrlsArray, childrenUrlsArray):
    inputJsonObj = json.loads(inputJson)
    if (("_embedded" in inputJsonObj) & ("terms" in inputJsonObj["_embedded"])):
        termsList = inputJsonObj["_embedded"]["terms"]
        for term in termsList:
            if (("label" in term)):
                termName = term["label"]
                # print(termName)

            if (("_links" in term)):
                # pprint.pprint(term["_links"])

                if (("jstree" in term["_links"])):
                    if ("href" in term["_links"]["jstree"]):
                        jsTreeUrl = term["_links"]["jstree"]["href"] + "?viewMode=All&siblings=false"
                        jsTreeUrlsArray.append(jsTreeUrl)
                # else:
                #     keep an eye out for "is_root" and "is_obsolete"
                if (("children" in term["_links"])):
                    if ("href" in term["_links"]["children"]):
                        childrenUrl = term["_links"]["children"]["href"]
                        childrenUrlsArray.append(childrenUrl)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(start_async_process())
    loop.run_until_complete(future)

# # https://www.ebi.ac.uk/ols/ontologies/mondo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMONDO_0005812
# URL = "https://www.geeksforgeeks.org/data-structures/"
# r = requests.get(URL)
# html_doc = r.content
# soup = BeautifulSoup(html_doc, 'html5lib')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
