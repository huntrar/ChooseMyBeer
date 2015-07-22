
import sys

from alc_reference import get_alc_reference
from utils import get_html, is_num, unique



class Keg(object):
    def __init__(self, url):
        ''' url is a Bevmo page with a single beer listed
        
            parse(url) retrieves the page and parses the contents into the following members

                self.name    (may include brewery/brand and/or beer)
                self.price
                self.volume
                self.num_avail
                self.desc
        '''
        self.url = url
        self.parse(url)


    def open():
        webbrowser.open(url)


    def parse(url):
        html = get_html(url)

        ''' Attempt to get name and volume and return if either fails '''
        try:
            name = html.xpath('//h1/text()')[0].strip()
        except Exception as e:
            sys.stderr.write(str(e)+'\n')
            return

        if '(' in name and ')' in name:
            try:
                split_name = name.split('(')
                name = split_name[0].strip()
                volume = filter(lambda x: isinstance(x, is_num), split_name[1].strip(')')).strip()
            except Exception as e:
                sys.stderr.write(str(e)+'\n')
                return
        else:
            ''' Failed to retrieve volume, which is necessary for computation '''
            return
            
        print name, volume
        
        ''' Attempt to get price and return if it fails '''
        try:
            self.price = html.xpath('//span[@class="ProductDetailItemPrice"]/text()')[0].strip()
        except Exception as e:
            sys.stderr.write(str(e)+'\n')
            return
       
        ''' Attempt to get number of available kegs '''
        try:
            self.num_avail = html.xpath('//em/text()')[0].strip()
        except Exception as e:
            self.num_avail = ''
        
        ''' Attempt to get description '''
        try:
            self.desc = html.xpath('//td[@class="ProductDetailCell"]/p/text()')[0].strip()
        except Exception as e:
            self.desc = ''



