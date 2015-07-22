
import sys
import webbrowser

from alc_reference import get_alc_reference
from utils import get_html, is_num, unique



class BeerKeg(object):
    ''' Self-parsing Beer Keg class given a url '''
    def __init__(self, url, verbose=False):
        ''' url must be a string containing the url for a single BevMo keg '''
        self.url = url

        ''' verbose is a flag that prints the contents of the Beer object during parsing '''
        self.verbose = verbose

        ''' parse(url) retrieves the page and parses the contents into the following fields

                self.name    (may include brewery/brand and/or beer)
                self.price   (USD)
                self.volume  (Gallons)
                self.num_avail  (kegs)
                self.desc    (keg description)
        '''
        self.parse(url)


    def open(self):
        webbrowser.open(url)


    def get_ratio(self, alcohol_pct):
        ''' Returns the volume of alcohol per USD '''
        return (alcohol_pct * .1 * self.volume) / self.price


    def parse(self, url):
        html = get_html(url)

        ''' Attempt to get name and volume and return if either fails '''
        try:
            self.name = html.xpath('//h1/text()')[0].strip()
            if '(' in self.name and ')' in self.name:
                    split_name = self.name.split('(')
                    self.name = split_name[0].strip()
                    self.volume = float(filter(lambda x: is_num(x.replace('.', '')), split_name[1].strip(')').strip()))

                    if self.verbose:
                        sys.stderr.write(self.name + ', ')
                        sys.stderr.write(str(self.volume) + ', ')
            else:
                ''' Failed to retrieve volume, which is necessary for computation '''
                sys.stderr.write('Failed to retrieve volume!')
                return
        except Exception as e:
            assert e
            
        ''' Attempt to get price and return if it fails '''
        try:
            self.price = float(html.xpath('//span[@class="ProductDetailItemPrice"]/text()')[0].strip())

            if self.verbose:
                sys.stderr.write(str(self.price) + ', ')
        except Exception as e:
            assert e
       
        ''' Attempt to get number of available kegs '''
        try:
            self.num_avail = int(html.xpath('//em/text()')[0].strip().split()[0])

            if self.verbose:
                sys.stderr.write(str(self.num_avail) + '\n')
        except Exception as e:
            self.num_avail = ''
        
        ''' Attempt to get description '''
        try:
            self.desc = html.xpath('//td[@class="ProductDetailCell"]/p/text()')[0].strip()
        except Exception as e:
            self.desc = ''


