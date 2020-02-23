import exceptions
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup

PARSERS = ['lxml', 'html.parser', 'html5lib']

def find_links(text): #Expects list of strings
    links = []

    soup = None
    count = 0
    
    while soup == None:        
        if count >= len(PARSERS):
            raise exceptions.NoParserException()
        
        try:
            soup = BeautifulSoup(text, PARSERS[count])
        except Exception as e:
            print(text)
            raise e
            if count < len(PARSERS)-1:
                print(PARSERS[count], "not found, trying", PARSERS[count+1])
            else:
                print(PARSERS[count], "not found, cannot continue.")
            count += 1
    
    for link in soup.find_all('a'):
        url = link.get('href')

        if url == None:
            continue

        parse_data = urlparse(url)

        if parse_data.scheme == "http" or parse_data.scheme == "https":
            msg = parse_data.scheme+"://"+parse_data.netloc+parse_data.path               
            links.append(msg)

    return links

def load_webpage(url, logging=None):
    try:
        page = urllib.request.urlopen(url)
        
        raw = page.read()


        return raw
    
    except Exception as e:
        if logging:
            with open(logging, 'a') as file:
                file.write(str(e))
        return ""

def get_domain_name(full_url):
    parse_data = urlparse(full_url)
    return parse_data.scheme+"://"+parse_data.netloc

def extract_keywords(url):
    parse_data = urlparse(url)

    keywords = []

    split = parse_data.netloc.split('.')[:-1]

    for keyword in split:
        if keyword != "www":
            keywords.append(keyword)

    return keywords
        
