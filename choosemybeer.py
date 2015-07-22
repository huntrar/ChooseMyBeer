#!/usr/bin/env python

#############################################################
#                                                           #
# ChooseMyBeer - find the beer that's right for you         #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import sys
from urlparse import urlparse
import requests
import webbrowser

from alc_reference import get_alc_reference
from beer import Beer
from utils import get_html, is_num, unique

import lxml.html as lh


def get_bevmo_beers():
    '''     For info on XPaths, see:

            http://www.w3schools.com/xpath/xpath_syntax.asp
    '''
    seed_url = "http://www.bevmo.com/Shop/ProductList.aspx/Beer/Kegs/_/N-15Z1z141vn?DNID=Beer"
    base_url = '{url.scheme}://{url.netloc}'.format(url=urlparse(seed_url))

    ''' Unique new page links with their base url appended '''
    new_page_links = []
    new_page_links[:] = unique(get_html(seed_url).xpath('//div[@class="ProductListPaging"]/a/@href'))
    page_links = map(lambda x: base_url + x, new_page_links)

    ''' Lists for holding links to individual beer kegs '''
    new_beer_links = []
    beer_links = []

    ''' List to hold Beer keg objects '''
    beers = []
    while len(page_links) > 0:
        ''' Links are removed as they are crawled '''
        page_link = page_links.pop(0)

        ''' Beer keg links '''
        new_beer_links[:] = unique(get_html(page_link).xpath('//a[@class="ProductListItemLink"]/@href'))
        beer_links += map(lambda x: base_url + x, new_beer_links)
        for link in beer_links:
            beers.append(Beer(link, verbose=True))

        try:
            ''' A typical link looks like Shop/ProductList.aspx/_/N-15Z1z141vn/No-100?DNID=Beer

                If the number following No- is evenly divisible by 100 it leads to more pages

            '''
            if 'No-' in page_link and (page_link.split('No-')[1].split('?')[0] % 100) == 0:
                ''' Unique new page links with their base url appended '''
                new_page_links[:] = unique(get_html(page_link).xpath('//div[@class="ProductListPaging"]/a/@href'))
                page_links += map(lambda x: base_url + x, new_page_links)
        except Exception as e:
            assert e

    return beers


def run():
    ''' alc_ref format is: {'Brewery/Brand' : {'Beer' : 'Alcohol %'}}

        Access alcohol percentage using alc_ref['brand']['beer']
    '''
    #alc_ref = get_alc_reference()

    ''' Currently prints the contents of the alcohol reference dict '''
    '''
    for brand in alc_ref.iterkeys():
        for beer in alc_ref[brand].iterkeys():
            print brand + ',', beer + ',', alc_ref[brand][beer] + '%'
    '''

    ''' members in Beer object:

            self.name    (may include brewery/brand and/or beer)
            self.price
            self.volume
            self.num_avail
            self.desc
    '''
    beers = get_bevmo_beers()
    print 'Printing beers'
    for b in beers:
        print b.name, b.price, b.volume, b.num_avail, b.desc 



if __name__ == '__main__':
    run()

