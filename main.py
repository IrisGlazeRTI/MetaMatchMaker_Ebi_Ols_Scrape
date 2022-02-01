import requests
from bs4 import BeautifulSoup

# soup = BeautifulSoup(html_doc, 'html.parser')

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def getAllTermJson():
    # TODO
    return ""

def writeAllJsTree(term):
    # TODO
    return None

def writeTextToFile(outputFileName, text):
    # TODO
    return None

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # https://www.ebi.ac.uk/ols/ontologies/mondo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMONDO_0005812
    URL = "https://www.geeksforgeeks.org/data-structures/"
    r = requests.get(URL)
    # print(r.content)
    html_doc = r.content
    soup = BeautifulSoup(html_doc, 'html5lib')
    print(soup.prettify())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
