#!/usr/bin/env python

#############################################################
#                                                           #
# ChooseMyBeer - find the beer that's right for you         #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import sys

from alc_reference import get_alc_reference
from utils import get_html, is_num, unique

import lxml.html as lh


def run():
    alc_ref = get_alc_reference()

    ''' Currently prints the contents of the alcohol reference dict '''
    for brand in alc_ref.iterkeys():
        for beer in alc_ref[brand].iterkeys():
            print brand + ',', beer + ',', alc_ref[brand][beer] + '%'



if __name__ == '__main__':
    run()

