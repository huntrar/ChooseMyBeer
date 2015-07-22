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
from keg import Keg
from utils import get_html, is_num, unique

import lxml.html as lh


def get_bevmo_beers():
    seed_url = "http://www.bevmo.com/Shop/ProductList.aspx/Beer/Kegs/_/N-15Z1z141vn?DNID=Beer"
    seed_html = get_url(seed_url)

    ''' Get page links from seed_url

        For info on XPaths, see:
            http://www.w3schools.com/xpath/xpath_syntax.asp
    '''
    links = seed_html.xpath('//div[@class="ProductListPaging"]/a/@href')



def run():
    ''' alc_ref format is: {'Brewery/Brand' : {'Beer' : 'Alcohol %'}}

        Access alcohol percentage using alc_ref['brand']['beer']
    '''
    alc_ref = get_alc_reference()

    ''' Currently prints the contents of the alcohol reference dict '''
    for brand in alc_ref.iterkeys():
        for beer in alc_ref[brand].iterkeys():
            print brand + ',', beer + ',', alc_ref[brand][beer] + '%'



if __name__ == '__main__':
    run()

