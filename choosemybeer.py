#!/usr/bin/env python

#############################################################
#                                                           #
# ChooseMyBeer - find the keg that's right for you          #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import argparse
import heapq
from urlparse import urlparse

from beerkeg import BeerKeg
from utils import get_html, is_num, unique

import lxml.html as lh


def get_parser():
    parser = argparse.ArgumentParser(description='find the keg that\'s right '
                                                 'for you')
    parser.add_argument('-a', '--attempts', type=int, nargs='?',
                        help='number of attempts to resolve each ABV '
                             '(default: 10)')
    parser.add_argument('-f', '--filter', type=str, nargs='*',
                        help='find kegs with descriptions matching these '
                             'keywords')
    parser.add_argument('-l', '--limit', type=int, nargs='?',
                        help='limit number of kegs to crawl (default: 10000)')
    parser.add_argument('-p', '--price', type=float, nargs='?',
                        help='limit the price range')
    parser.add_argument('-t', '--top', type=int, nargs='?',
                        help='number of top kegs to display (default: 3)')
    parser.add_argument('-u', '--unfilter', type=str, nargs='*',
                        help='find kegs with descriptions not matching these '
                             'keywords')
    return parser


def get_optimal_kegs(args):
    ''' Gets kegs from bevmo.com
        finds the kegs with the optimal gallons of alcohol per USD
    '''
    num_kegs = args['top']
    beer_limit = args['limit']
    num_attempts = args['attempts']
    max_price = args['price']
    desc_filter = args['filter']
    desc_unfilter = args['unfilter']

    ''' The first url to crawl and its base url '''
    seed_url = 'http://www.bevmo.com/Shop/ProductList.aspx/\
                Beer/Kegs/_/N-15Z1z141vn?DNID=Beer'
    base_url = '{url.scheme}://{url.netloc}'.format(url=urlparse(seed_url))

    ''' Get initial unique page links from the seed url
        append base_url to them
    '''

    '''     For info on XPaths, see:
            http://www.w3schools.com/xpath/xpath_syntax.asp
    '''
    init_page_links = []
    init_page_links[:] = unique(get_html(seed_url).xpath('//div[@class="Product\
                                                         ListPaging"]/a/@href'))

    if not init_page_links:
        print('Failed to retrieve the initial keg page links!')
        return None

    ''' Lists for holding links to pages of beer kegs '''
    page_links = [seed_url] + map(lambda x: base_url + x, init_page_links)
    new_page_links = []

    ''' Lists for holding links to individual beer kegs '''
    beer_links = []
    new_beer_links = []

    ''' To keep track of already crawled beer kegs '''
    crawled_beers = set()

    ''' List for matching --filter and --unfilter keyword arguments to
        keg descriptions
    '''
    matched = []

    ''' List to hold top beer kegs, the size of optimal_kegs is limited by the
        num_kegs argument
    '''
    optimal_kegs = []

    keg = None
    while len(page_links) > 0 and len(crawled_beers) < beer_limit:
        ''' Links are removed as they are crawled '''
        page_link = page_links.pop(0)

        ''' Beer keg links '''
        new_beer_links[:] = unique(get_html(page_link).xpath('//a[@class="Prod\
                                                             uctListItemLink"]\
                                                             /@href'))
        beer_links += [base_url + x for x in new_beer_links]

        ''' Crawl the beer keg links
            get the gallons of alcohol/USD ratio
        '''
        for link in beer_links:
            ''' Break if the number of crawled beers exceeds the limit '''
            if len(crawled_beers) >= beer_limit:
                break

            ''' Cache the BevMo beer id's to prevent duplicates '''
            beer_id = link.split('/')[-1]

            if beer_id not in crawled_beers:
                ''' Create BeerKeg object '''
                keg = BeerKeg(link, num_attempts, verbose=True)

                ''' Call keg.parse() then filter kegs by their descriptions
                    Calling keg.parse() produces fields keg.desc, keg.price, etc
                    keg.parse() will only parse once per keg object
                '''

                ''' Check if price is within range if one was given '''
                if max_price:
                    keg.parse()

                    if keg.price > max_price:
                        ''' Move onto the next keg and ignore this one '''
                        continue

                ''' args['filter'] has words that must be in the description '''
                ''' desc_filter has words that must be in the description '''
                if desc_filter:
                    keg.parse()

                    matched = [word in keg.desc for word in desc_filter]

                    ''' All keywords must be present for a match '''
                    if not all(matched):
                        ''' Move onto the next keg and ignore this one '''
                        continue

                ''' desc_unfilter has words that can't be in the description '''
                if desc_unfilter:
                    keg.parse()

                    matched = [word in keg.desc for word in desc_unfilter]

                    ''' Any keyword must be present to nullify a match '''
                    if any(matched):
                        ''' Move onto the next keg and ignore this one '''
                        continue

                ''' Add current beer to crawled beers '''
                crawled_beers.add(beer_id)

                ''' Print how many kegs have been crawled '''
                print('Keg {}'.format(len(crawled_beers)))

                ''' Gets the gallons of alcohol per USD for the keg '''
                ratio = keg.get_ratio()

                print('')

                ''' Maintain a sorted list of the current top 3 kegs using
                    heapq (heap queue algorithm)

                    optimal_kegs holds a tuple containing the ratio and keg
                    associated with it
                '''
                if optimal_kegs:
                    for opt_tuple in optimal_kegs:
                        ''' If ratio is greater than any keg ratio currently
                            in optimal_kegs, then add it
                        '''
                        if ratio > opt_tuple[0]:
                            if len(optimal_kegs) >= num_kegs:
                                ''' Adds new item to list
                                    removes the smallest to maintain size
                                '''
                                heapq.heappushpop(optimal_kegs, (ratio, keg))
                            else:
                                heapq.heappush(optimal_kegs, (ratio, keg))
                            break
                else:
                    ''' Will only occur for the very first keg crawled '''
                    heapq.heappush(optimal_kegs, (ratio, keg))

        ''' Typical link: Shop/ProductList.aspx/_/N-15Z1z141vn/No-100?DNID=Beer

            If No- is evenly divisible by 100, it leads to more pages to add
        '''
        if 'No-' in page_link:
            if int(page_link.split('No-')[1].split('?')[0]) % 100 == 0:
                ''' Unique new page links with their base url appended '''
                new_page_links[:] = unique(get_html(page_link).xpath('//div[@cl\
                                                                     ass="Produ\
                                                                     ctListPagi\
                                                                     ng"]/a/@hr\
                                                                     ef'))
                page_links += [base_url + x for x in new_page_links]

    ''' Sort the list in descending order by ratio
        (index 0 in the keg tuple)
    '''
    return sorted(optimal_kegs, key=lambda x: x[0], reverse=True)


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    ''' Number of top kegs to display (default: 3) '''
    if not args['top']:
        args['top'] = 3

    ''' Number of keg pages to crawl (default: 10000) '''
    if not args['limit']:
        args['limit'] = 10000

    ''' Number of attempts to resolve each ABV (default: 10) '''
    if not args['attempts']:
        args['attempts'] = 10

    optimal_kegs = get_optimal_kegs(args)

    ratio = 0
    keg = None

    try:
        ''' Print a menu for the user to choose from the top kegs '''
        printing = True
        optimal_keg = None
        chosen_keg = -1
        quit = 0

        if not optimal_kegs:
            print('An error occurred during processing. \
                  Check your internet connection.')
        else:
            ''' Loop until user decides to quit '''
            while printing and chosen_keg != quit:
                ''' keg_tuple is ratio followed by BeerKeg object '''
                for i, keg_tuple in enumerate(optimal_kegs):
                    ratio = keg_tuple[0]
                    keg = keg_tuple[1]

                    print('\n{}. {}\tRatio: {}'.format(i, keg.name, ratio))
                    print('Available: {}\tVolume: {} Gal.\tPrice: ${}\n{}\
                          '.format(keg.num_avail, keg.volume, \
                                   keg.price, keg.desc))

                    ''' Make quit always be the last menu option '''
                    quit = i+1
                print('\n{}. Quit'.format(quit))

                try:
                    chosen_keg = int(raw_input('Choose a keg: '))
                except Exception:
                    continue

                ''' If chosen keg is within the optimal kegs range
                    (quit is one outside), then open the link
                '''
                if chosen_keg >= 0 and chosen_keg < len(optimal_kegs):
                    optimal_keg = optimal_kegs[chosen_keg][1]

                    ''' Opens the link to the keg in a browser
                        using webbrowser
                    '''
                    optimal_keg.open()

    except KeyboardInterrupt:
        pass



if __name__ == '__main__':
    command_line_runner()

