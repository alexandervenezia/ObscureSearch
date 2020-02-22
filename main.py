import loading
import time
import queue

class ObscureSearch(object):
    def __init__(self):
        self.keywords = {} #Keywords in URLs, hashed to number of occurrences. We prefer URLs without many keywords we've already seen
        self.indexed = {} #Web pages indexed, hashed to the number of times they have been indexed
        self.leaves = queue.Queue() #All leaf "nodes," URLs scraped from indexed websites which have not themselves been indexed

    def index_page(self, url):
        if url in self.indexed:
            self.indexed[url] += 1
            return

        text = loading.load_webpage(url)

        
        for link in loading.find_links(text):
            domain = loading.get_domain_name(link)
            if domain in self.indexed:
                self.indexed[domain] += 1
                continue

            self.indexed[domain] = 1
            self.leaves.put(link)


    def search(self, start_url, max_nodes, max_time): #max_time in seconds
        start_time = time.time()
        start_nodes = len(self.indexed)

        self.index_page(start_url)

        while True:
            current_time = time.time()

            elapsed_time = current_time-start_time

            if elapsed_time > max_time:
                break

            if len(self.indexed)-start_nodes > max_nodes:
                break

            if self.leaves.empty():
                break

            leaf = self.leaves.get()

            self.index_page(leaf)

    def get_obscure(self, num_lowest): #num_lowest = how many results to return. If it is greater than the number of sites indexed, all sites will be returned.
        ordered_sites = []

        for site in self.indexed:
            ordered_sites.append((site, self.indexed[site]))

        ordered_sites.sort(key=lambda tuple: tuple[1])

        return ordered_sites[0:num_lowest]
            


