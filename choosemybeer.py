#!/usr/bin/env python

#############################################################
#                                                           #
# ChooseMyBeer - find the beer that's right for you         #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

from collections import OrderedDict
import random
import requests
import string
import sys

import lxml.html as lh


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
                'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
                'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5')


def get_html(url):
    try:
        # Get HTML response
        headers={'User-Agent' : random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers)
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as e:
        sys.stderr.write('Failed to retrieve {}.\n'.format(url))
        sys.stderr.write(str(e))
        return None


def is_num(num):
    ''' Values to ignore when checking if value is a number '''
    ignore = ['-', '<', '>']
    try:
        for sym in ignore:
            if sym in num:
                num = num.replace(sym, '')
        n = float(num)
        return True
    except ValueError:
        return False


def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item


def filter_ref_text(ref_text):
    ''' Strip whitespace and remove empty strings '''
    stripped_text = filter(None, map(lambda x: x.strip() if isinstance(x, str) else x, ref_text))

    ''' Filter unprintable characters '''
    return [filter(lambda x: x in string.printable, entry) for entry in stripped_text]


def structure_ref_text(ref_text): 
    ''' ref_text format: [Brewery/Brand, Beer, Alcohol %, Calories, Carbs]

        We must filter Calories and Carbs from the data for being both inconsistent and currently unuseful
    
        Our first rule for correcting the data is ensuring only a single number follows a non-number string

        i.e., if the previous entry was a number, do not append until there is a non-number string
    ''' 
    filtered_text = []
    prev_was_num = False
    
    for entry in ref_text:
        if is_num(entry):
            if prev_was_num:
                ''' Skip appending this entry '''
                continue
            else:
                prev_was_num = True
                filtered_text.append(entry)
        else:
            prev_was_num = False
            filtered_text.append(entry)
    
    ''' To complete structuring of the data, each line should be two strings followed by a number

        To fix malformed data, we can take advantage of the fact that an extra string is often equal to a string on the same line and just filter for duplicates
    '''
    structured_text = []
    line = []

    ''' Split text by line using number values as separators '''
    for entry in filtered_text:
        line.append(entry)

        if is_num(entry):
            if len(line) == 3:
                ''' We can expect a line of length 3 to be structured '''
                structured_text += line
            else:
                ''' Attempt to correct malformed line by filtering duplicates '''
                line[:] = unique(line)
                if len(line) == 3:
                    structured_text += line
            line = []
    return structured_text


def make_ref_dict(unstructured_text):
    ''' Structure the text before converting to dictionary '''
    structured_text = structure_ref_text(unstructured_text)

    ''' Now we construct our reference dictionary using our now structured data

        Data format is: {'Brewery/Brand' : {'Beer' : 'Alcohol %'}}
    '''
    ref_dict = OrderedDict()
    while len(structured_text) > 2:
        ''' Remove entries from the head of the structured text list in order of our desired structure '''
        brand = structured_text.pop(0)
        beer = structured_text.pop(0)
        alcohol_pct = structured_text.pop(0)

        ''' If brand not already in reference dictionary, initialize an OrderedDict

            One can reference a specific brand and beer and receive its alcohol content like so:
            
            ref_dict['brand']['beer']
        '''
        if brand not in ref_dict:
            ref_dict[brand] = OrderedDict()
        ref_dict[brand][beer] = alcohol_pct
        
    return ref_dict


def get_alc_reference():
    ''' Return an alcohol reference dictionary from realbeer.com
    
        Reference includes Brewery/Brand, Beer, and Alcohol %
    '''

    pages = []
    pages.append(get_html("http://www.realbeer.com/edu/health/calories.php"))
    pages.append(get_html("http://www.realbeer.com/edu/health/calories2.php"))

    pages_text = []
    for page in pages:
        '''
            An XPath is used to extract the tags we need, which is determined by looking at the page source

            See: http://www.w3schools.com/xpath/xpath_syntax.asp
        '''
        pages_text += page.xpath('//table[@cellpadding="2"][2]/tr/td//text()')

    ''' Filter the data and return the proper reference dictionary '''
    return make_ref_dict(filter_ref_text(pages_text))


def run():
    alc_ref = get_alc_reference()

    ''' Currently prints the contents of the alcohol reference dict '''
    for brand in alc_ref.iterkeys():
        for beer in alc_ref[brand].iterkeys():
            print brand + ',', beer + ',', alc_ref[brand][beer] + '%'



if __name__ == '__main__':
    run()

