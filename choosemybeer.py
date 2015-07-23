#!/usr/bin/env python

#############################################################
#                                                           #
# ChooseMyBeer - find the beer that's right for you         #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import heapq
import sys
from urlparse import urlparse

from alc_reference import get_alc_reference
from beerkeg import BeerKeg
from utils import get_html, is_num, unique

import lxml.html as lh


def get_optimal_keg(num_kegs, page_limit=10000):
    ''' Gets kegs from BevMo and cross references them with Realbeer beers and their alcohol percentages

        num_kegs is the number of optimal kegs to return and page_limit is the max number of keg pages to crawl

        Returns the kegs with the highest ratio of gallons of alcohol per dollar
    '''

    ''' The first url to crawl and its base url '''
    seed_url = "http://www.bevmo.com/Shop/ProductList.aspx/Beer/Kegs/_/N-15Z1z141vn?DNID=Beer"
    base_url = '{url.scheme}://{url.netloc}'.format(url=urlparse(seed_url))

    ''' Initialize unique page links taken from the seed url
    
        The base url is then appended to links as they have no domain
    '''
    init_page_links = []

    '''     For info on XPaths, see:

            http://www.w3schools.com/xpath/xpath_syntax.asp
    '''
    init_page_links[:] = unique(get_html(seed_url).xpath('//div[@class="ProductListPaging"]/a/@href'))
    page_links = [seed_url] + map(lambda x: base_url + x, init_page_links)
    new_page_links = []

    ''' Lists for holding links to individual beer kegs '''
    new_beer_links = []
    beer_links = []
    
    ''' To keep track of already crawled beers '''
    crawled_beers = set()

    ''' List to hold top beer kegs, the size of optimal_kegs is limited by the num_kegs argument '''
    optimal_kegs = []

    ''' The alcohol reference dictionary, where the alcohol percentages reside '''
    alc_ref = get_alc_reference()

    keg = None
    while len(page_links) > 0 and len(crawled_beers) < page_limit:
        ''' Links are removed as they are crawled '''
        page_link = page_links.pop(0)

        ''' Beer keg links '''
        new_beer_links[:] = unique(get_html(page_link).xpath('//a[@class="ProductListItemLink"]/@href'))
        beer_links += map(lambda x: base_url + x, new_beer_links)

        ''' Crawl the beer keg links and get the gallons of alcohol/dollar ratio '''
        for link in beer_links:
            beer_id = link.split('/')[-1]
            if beer_id not in crawled_beers:
                crawled_beers.add(beer_id)

                keg = BeerKeg(link, verbose=True)

                ''' Gets the gallons of alcohol per dollar ratio for the keg '''
                ratio = keg.get_ratio(alc_ref)

                ''' Maintain a sorted list of the current top 3 kegs using heapq (heap queue algorithm)
                
                    optimal_kegs holds a tuple containing the ratio and keg associated with it
                '''
                if optimal_kegs:
                    for opt_tuple in optimal_kegs:
                        ''' If ratio is greater than any keg ratio currently in optimal_kegs then add it '''
                        if ratio > opt_tuple[0]:
                            if len(optimal_kegs) >= num_kegs:
                                ''' Adds new item to list and removes the smallest to maintain proper size '''
                                heapq.heappushpop(optimal_kegs, (ratio, keg)) 
                            else:
                                heapq.heappush(optimal_kegs, (ratio, keg)) 
                            break
                else:
                    ''' Will only occur for the very first keg crawled '''
                    heapq.heappush(optimal_kegs, (ratio, keg))

        ''' A typical link looks like Shop/ProductList.aspx/_/N-15Z1z141vn/No-100?DNID=Beer

            If the number following No- is evenly divisible by 100, it leads to more pages which are then added
        '''
        if 'No-' in page_link and int(page_link.split('No-')[1].split('?')[0]) % 100 == 0:
            ''' Unique new page links with their base url appended '''
            new_page_links[:] = unique(get_html(page_link).xpath('//div[@class="ProductListPaging"]/a/@href'))
            page_links += map(lambda x: base_url + x, new_page_links)

    ''' Sort the list in descending order by ratio (index 0 in the keg tuple)  '''
    return sorted(optimal_kegs, key=lambda x: x[0], reverse=True)


def run():
    ''' Get the top 3 optimal kegs, you can also pass an optional page limit argument for testing '''
    optimal_kegs = get_optimal_keg(num_kegs=3)

    ratio = 0
    keg = None

    try:
        printing = True
        optimal_keg = None
        chosen_keg = -1
        quit = 0

        ''' Loop until user decides to quit '''
        while printing and chosen_keg != quit:
            ''' keg_tuple is ratio followed by BeerKeg object '''
            for i, keg_tuple in enumerate(optimal_kegs):
                ratio = keg_tuple[0]
                keg = keg_tuple[1]

                print('\n{}. {}\tRatio: {}'.format(i, keg.name, ratio))
                print('Available: {}\tVolume: {} Gal.\tPrice: ${}\n{}'.format(keg.num_avail, keg.volume, keg.price, keg.desc))

                ''' Make quit always be the last menu option '''
                quit = i+1
            print('\n{}. Quit'.format(quit))

            try:
                chosen_keg = int(raw_input('Choose a keg: '))
            except Exception:
                continue

            ''' If chosen keg is within the optimal kegs range (quit is one outside), then open the link '''
            if chosen_keg >= 0 and chosen_keg < len(optimal_kegs):
                optimal_keg = optimal_kegs[chosen_keg][1]

                ''' Opens the link to the keg in a browser using webbrowser '''
                optimal_keg.open()

    except KeyboardInterrupt:
        sys.exit()



if __name__ == '__main__':
    run()

