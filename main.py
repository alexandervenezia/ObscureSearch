import loading
import time
import queue
import threading

COMMON = [
    "https://www.reddit.com", "https://twitter.com", "https://www.facebook.com",
    "https://www.google.com", "https://www.youtube.com", "https://amazon.com",
    ]

http_common = []

for url in COMMON:
    http = url[:4]+url[5:]
    http_common.append(http)

COMMON.extend(http_common)

class ObscureSearch(object):   
    def __init__(self):
        self.keywords = {"reddit" : 1000} #Keywords in URLs, hashed to number of occurrences. We prefer URLs without many keywords we've already seen
        self.indexed = {} #Web pages indexed, hashed to the number of times they have been indexed
        self.exact_urls = set()
        self.start_urls = set()
        self.common_domains = set(COMMON)
        self.leaves = queue.Queue() #All leaf "nodes," URLs scraped from indexed websites which have not themselves been indexed
        self.total_loaded = 0
        
    def count_keywords(self, link):
        keywords = loading.extract_keywords(link)

        count = 0

        for keyword in keywords:
            if keyword in self.keywords:
                count += self.keywords[keyword]
                self.keywords[keyword] += 1
            else:
                self.keywords[keyword] = 1

        return count

    def index_page(self, url, max_keywords, max_in_domain):
        if url in self.indexed:
            self.indexed[url] += 1
            return

        self.total_loaded += 1
        text = loading.load_webpage(url)

        for link in loading.find_links(text):
            domain = loading.get_domain_name(link)

            if domain in self.common_domains:
                continue
            
            if domain in self.indexed:                
                self.indexed[domain] += 1

                if self.indexed[domain] > max_in_domain or link in self.exact_urls:
                    continue

            if self.count_keywords(link) > max_keywords:
                continue
           
                
            self.exact_urls.add(link)
            self.indexed[domain] = 1


            self.leaves.put(link)



    def search(self, start_url, max_nodes, max_time, max_keywords=5, iterations=1, reset_num=5, max_in_domain=5): #max_time in seconds, TOTAL
        start_time = time.time()
        start_nodes = len(self.indexed)

        self.index_page(start_url, max_keywords, max_in_domain)
        for i in range(iterations):
            while True:
                current_time = time.time()

                elapsed_time = current_time-start_time

                if elapsed_time > max_time:
                    break

                if len(self.indexed)-start_nodes > max_nodes:
                    break
                
                if self.leaves.empty():
                    continue                

                leaf = self.leaves.get()

                
                self.index_page(leaf, max_keywords, max_in_domain)

                
            self.leaves = queue.Queue()
            for leaf in self.get_obscure(reset_num, self.start_urls):
                self.leaves.put(leaf[0])
                self.start_urls.add(leaf[0])
            
            

    def get_obscure(self, num_lowest, excluded=set()): #num_lowest = how many results to return. If it is greater than the number of sites indexed, all sites will be returned.
        ordered_sites = []

        for site in self.indexed:
            ordered_sites.append((site, self.indexed[site]))

        ordered_sites.sort(key=lambda tuple: tuple[1])

        obscure = []
        n = 0
        
        for site in ordered_sites:
            if n > num_lowest:
                break
            if not site in excluded:
                obscure.append(site)
                n += 1
        
        return ordered_sites[0:num_lowest]
            

search = ObscureSearch()
