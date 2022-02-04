import requests
import asyncio
import json
import pprint
import time
import csv
import sys
import getopt
# import pandas as pd

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

FILENAME_JSTREE_URLS = "js_tree_urls_output.tsv"
FILENAME_CHILDREN_URLS = "children_urls_output.tsv"
FILENAME_TREES_CONTENTS_TSV = "trees_contents.tsv"

def request(session, url, identifyingVal):
    # URL for API request to obtain the metadata based upon a study.
    # url = 'https://www.ebi.ac.uk/ols/api/terms?page=' + str(pageNum) + '&size=1000'
    with session.get(url) as response:
        data = response.text

        if response.status_code != 200:
            print("FAILURE::{0}".format(url))
            data = ""
        else:
            print("SUCCESS::{0}".format(identifyingVal))

        # elapsed_time = default_timer() - START_TIME
        # completed_at = "{:5.2f}s".format(elapsed_time)
        # print("{0:<30} {1:>20}".format(identifyingVal, completed_at))
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

async def start_async_process(jsTreeUrlsArray, childrenUrlsArray):
    results = []
    # jsTreeUrlsArray = []
    # childrenUrlsArray = []
    # pagesArray = [0, 1, 2]
    #pagesArray = list(range(0, 4))
    pagesArray = list(range(0, 7156))
    pagesArray = pagesArray[0:100]
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
                jsTreeUrlsSubArr = extractTermApiUrlsArray(inputJson, "jstree")
                childrenUrlsSubArr = extractTermApiUrlsArray(inputJson, "children")
                jsTreeUrlsArray += jsTreeUrlsSubArr
                childrenUrlsArray += childrenUrlsSubArr

                pass
    jsTreeUrlsArray = list(set(jsTreeUrlsArray))
    childrenUrlsArray = list(set(childrenUrlsArray))
    return None

async def start_async_process_tree_contents(urlsArray, funcExtractTextArrFromJson, treeTextContentsArr):
    # urlsArray = urlsArray[0:5]
    # treeTextContentsArr = []
    with ThreadPoolExecutor(max_workers=1000) as executor:
        with requests.Session() as session:
            # asynchronously make an api call for each study
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    request,
                    *(session, url[0], url[0])
                )
                for url in urlsArray
            ]

            # Run once everything is complete.
            for response in await asyncio.gather(*tasks):
                inputJson = response
                treeWordsArr = funcExtractTextArrFromJson(inputJson)
                treeTextContentsArr += treeWordsArr
                pass
    treeTextContentsArr = list(set(treeTextContentsArr))
    print(treeTextContentsArr)
    return treeTextContentsArr

def extractJsTreeTermsWordsArr(inputJson):
    jsonObj = json.loads(inputJson)
    resultsArr = []
    for item in jsonObj:
        result = item.get("text")
        if (type(result) == str) & (result not in resultsArr):
            resultsArr.append(result)
    return resultsArr

def extractChildTermsWordsArr(inputJson):
    jsonObj = json.loads(inputJson)
    resultsArr = []
    if "_embedded" in jsonObj:
        if "terms" in jsonObj.get("_embedded"):
            jsonObjTerms = jsonObj.get("_embedded").get("terms")
            for item in jsonObjTerms:
                result = item.get("label")
                if (type(result) == str) & (result not in resultsArr):
                    resultsArr.append(result)
    return resultsArr

def writeAllJsTree(term):
    # TODO
    return None

def writeArrayToFile(outputFileName, valsArray):
    with open(outputFileName, 'wt') as f:
        tsv_writer = csv.writer(f, delimiter='\t')
        for val in valsArray:
            tsv_writer.writerow([val])
    return None

# categoryName: either "jstree" or "children"
def extractTermApiUrlsArray(inputJson, categoryName):
    inputJsonObj = json.loads(inputJson)
    jsTreeUrlsArray = []
    if ("_embedded" in inputJsonObj) & ("terms" in inputJsonObj["_embedded"]):
        termsList = inputJsonObj["_embedded"]["terms"]
        for term in termsList:
            if "_links" in term:
                if categoryName in term["_links"]:
                    if "href" in term["_links"][categoryName]:
                        jsTreeUrl = term["_links"][categoryName]["href"]
                        if categoryName == "jstree":
                            jsTreeUrl += "?viewMode=All&siblings=false"
                        jsTreeUrlsArray.append(jsTreeUrl)
    return jsTreeUrlsArray

def buildTermApiUrlsArrays(inputJson, jsTreeUrlsArray, childrenUrlsArray, tsvWriterJsTree, tsvWriterChildren):
    inputJsonObj = json.loads(inputJson)
    if ("_embedded" in inputJsonObj) & ("terms" in inputJsonObj["_embedded"]):
        termsList = inputJsonObj["_embedded"]["terms"]
        for term in termsList:
            if "label" in term:
                termName = term["label"]
                # print(termName)

            if "_links" in term:
                # pprint.pprint(term["_links"])

                if "jstree" in term["_links"]:
                    if "href" in term["_links"]["jstree"]:
                        jsTreeUrl = term["_links"]["jstree"]["href"] + "?viewMode=All&siblings=false"
                        if jsTreeUrl not in jsTreeUrlsArray:
                            jsTreeUrlsArray.append(jsTreeUrl)
                            tsvWriterJsTree.writerow([jsTreeUrl])
                # else:
                #     keep an eye out for "is_root" and "is_obsolete"
                if "children" in term["_links"]:
                    if "href" in term["_links"]["children"]:
                        childrenUrl = term["_links"]["children"]["href"]
                        if childrenUrl not in childrenUrlsArray:
                            childrenUrlsArray.append(childrenUrl)
                            tsvWriterChildren.writerow([childrenUrl])

def main(argv):
    print(sys.argv)

    writeUrls = True
    writeContents = True
    try:
        opts, args = getopt.getopt(argv, "u:c:", ["gatherUrls=", "writeTreesContents="])
    except getopt.GetoptError:
        print
        'main.py -u <writeUrls> -c <writeContents>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-u", "--gatherUrls"):
            if arg == "N":
                writeUrls = False
        elif opt in ("-c", "--writeTreesContents"):
            if arg == "N":
                writeContents = False

    print
    'Write urls? "', writeUrls

    if writeUrls:
        jsTreeUrlsArray = []
        childrenUrlsArray = []
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(start_async_process(jsTreeUrlsArray, childrenUrlsArray))
        loop.run_until_complete(future)
        writeArrayToFile(FILENAME_JSTREE_URLS, jsTreeUrlsArray)
        writeArrayToFile(FILENAME_CHILDREN_URLS, childrenUrlsArray)

    # Getting the urls saved in the two output files created earlier.
    savedJsTreeUrlsArr = []
    savedChildrenUrlsArr = []
    with open(FILENAME_JSTREE_URLS) as j_in_file, open(FILENAME_CHILDREN_URLS) as c_in_file:
        tsv_file_j = csv.reader(j_in_file, delimiter='\t')
        tsv_file_c = csv.reader(c_in_file, delimiter='\t')
        for line in tsv_file_j:
            print(line)
            savedJsTreeUrlsArr.append(line)
        for line in tsv_file_c:
            print(line)
            savedChildrenUrlsArr.append(line)

    #jstree_urls_df = pd.read_csv(FILENAME_JSTREE_URLS, sep='\t')
    #children_urls_df = pd.read_csv(FILENAME_CHILDREN_URLS sep='\t')

    if writeContents:
        treesContentsArray = []

        jsTreeContentsArr = []
        loop2 = asyncio.get_event_loop()
        future2 = asyncio.ensure_future(start_async_process_tree_contents(savedJsTreeUrlsArr, extractJsTreeTermsWordsArr, jsTreeContentsArr))
        loop2.run_until_complete(future2)

        childTreeContentsArr = []
        loop3 = asyncio.get_event_loop()
        future3 = asyncio.ensure_future(start_async_process_tree_contents(savedChildrenUrlsArr, extractChildTermsWordsArr, childTreeContentsArr))
        loop3.run_until_complete(future3)

        treesContentsArray += jsTreeContentsArr
        treesContentsArray += childTreeContentsArr
        treesContentsArray = list(set(treesContentsArray))
        writeArrayToFile(FILENAME_TREES_CONTENTS_TSV, treesContentsArray)

    print("Done.")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(sys.argv[1:])

# # https://www.ebi.ac.uk/ols/ontologies/mondo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMONDO_0005812
# URL = "https://www.geeksforgeeks.org/data-structures/"
# r = requests.get(URL)
# html_doc = r.content
# soup = BeautifulSoup(html_doc, 'html5lib')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
