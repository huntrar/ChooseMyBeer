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

from alc_reference import get_alc_reference
from beerkeg import BeerKeg
from utils import get_html, is_num, unique

import lxml.html as lh


def get_bevmo_kegs(limit=1000):
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

    ''' List to hold BeerKeg objects '''
    beer_kegs = []
    while len(page_links) > 0 and len(beer_kegs) < limit:
        ''' Links are removed as they are crawled '''
        page_link = page_links.pop(0)

        ''' Beer keg links '''
        new_beer_links[:] = unique(get_html(page_link).xpath('//a[@class="ProductListItemLink"]/@href'))
        beer_links += map(lambda x: base_url + x, new_beer_links)
        for link in beer_links:
            beer_kegs.append(BeerKeg(link, verbose=True))

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

    return beer_kegs


def get_optimal_keg(beer_kegs):
    ''' alc_ref format is: {'Brewery/Brand' : {'Beer' : 'Alcohol %'}}

        alc_ref['first brand letter']['brand']['beer'] to get alcohol %
    '''
    alc_ref = get_alc_reference()

    ''' Find most optimal, in-stock beer by alcohol in gallons per dollar
    
        We assume the first letter of the keg name and reference brand are equal
    
        Exploiting this and sorting the lists could improve lookup performance
    '''
    optimal_keg = None
    optimal_ratio = 0
    keg_ratio = 0
    for keg in beer_kegs:
        try:
            ''' Retrieve the reference dictionary subset by matching the first letter of the keg '''
            ''' Does not seem to work too well so far '''
            print 'checking keg {}'.format(keg.name)
            sub_alc_ref = alc_ref[keg.name[0]]
            print 'possible brands: '
            for brand in sub_alc_ref.iterkeys():
                if any(brand.split()) in keg.name:
                    print 'matched brand {} to keg {}'.format(brand, keg.name)
                    print 'possible beers: '
                    for beer in sub_alc_ref[brand].iterkeys():
                        if any(beer.split()) in keg.beer:
                            print 'matched beer {} to kegs {}'.format(beer, keg.beer)
                            keg_ratio = keg.get_ratio(sub_alc_ref[brand][beer])
                            if keg_ratio > optimal_ratio:
                                optimal_keg = keg
                                optimal_ratio = keg_ratio
                        else:
                            print beer, ',',
                    print '\n'
                else:
                    print brand, ',',
                print '\n'
        except Exception as e:
            assert e

    return optimal_keg, optimal_ratio


def run():
    ''' fields in BeerKeg object:

            self.name    (may include brewery/brand and/or beer)
            self.price   (USD)
            self.volume  (Gallons)
            self.num_avail  (kegs)
            self.desc    (keg description)

        Get beer keg info and sort it by name
    '''
    ''' Limit set to 50 for testing '''
    beer_kegs = sorted(get_bevmo_kegs(50), key=lambda x: x.name)

    ''' Print info of optimal beer keg and open page '''
    optimal_keg, optimal_ratio = get_optimal_keg(beer_kegs)
    try:
        print optimal_keg.name, 'Ratio: ', str(optimal_ratio), '\n', optimal_keg.desc
    except Exception as e:
        assert e



if __name__ == '__main__':
    run()

