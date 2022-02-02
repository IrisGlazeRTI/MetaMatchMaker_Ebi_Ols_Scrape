import requests
import json
import pprint
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# soup = BeautifulSoup(html_doc, 'html.parser')

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def getAllTermJson():
    # TODO. still not used.
    # https://www.ebi.ac.uk/ols/api/terms?page=0&size=1000
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            data = getPaginatedTermsJson(0, 1000, session)
            print("DATA: ")
            print(data)
    return ""

# Page numbers 0 - 7148. Size will be max of 1000; will probably make it be 1000 every time.
def getPaginatedTermsJson(pageNum, size, session):
    # TODO
    url = 'https://www.ebi.ac.uk/ols/api/terms?page=' + pageNum + '&size=1000' + size
    with session.get(url) as response:
        data = response.text

        if response.status_code != 200:
            print("FAILURE::{0}".format(url))
    return data

def writeAllJsTree(term):
    # TODO
    return None

def writeTextToFile(outputFileName, text):
    # TODO
    with open(outputFileName, 'w') as f:
        f.write(text)
    return None

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('input.json') as f:
        inputJson = json.load(f)
        if(("_embedded" in inputJson) & ("terms" in inputJson["_embedded"])):
            termsList = inputJson["_embedded"]["terms"]
            for term in termsList:
                if(("label" in term)):
                    termName = term["label"]
                    print(termName)

                if (("_links" in term)):
                    # pprint.pprint(term["_links"])
                    jsTreeUrlsArray = []
                    childrenUrlsArray = []
                    if (("jstree" in term["_links"])):
                        if("href" in term["_links"]["jstree"]):
                            jsTreeUrl = term["_links"]["jstree"]["href"] + "?viewMode=All&siblings=false"
                            print(jsTreeUrl)
                            jsTreeUrlsArray.append(jsTreeUrl)
                    if (("children" in term["_links"])):
                        if ("href" in term["_links"]["children"]):
                            childrenUrl = term["_links"]["children"]["href"]
                            print(childrenUrl)
                            childrenUrlsArray.append(childrenUrl)

    # https://www.ebi.ac.uk/ols/ontologies/mondo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMONDO_0005812
    URL = "https://www.geeksforgeeks.org/data-structures/"
    r = requests.get(URL)
    # print(r.content)
    html_doc = r.content
    soup = BeautifulSoup(html_doc, 'html5lib')
    # print(soup.prettify())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
