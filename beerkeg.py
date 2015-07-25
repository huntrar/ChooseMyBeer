
import webbrowser

from alc_reference import get_alc_reference
from utils import get_html, is_num, unique



class BeerKeg(object):
    ''' Beer Keg class
        
        parse() will retrieve the url and parse it into its relevant fields
    
        match() finds the proper alcohol percentage and will invoke parse() if not done already
        
        get_ratio() calls match() and returns the ratio of gallons of alcohol per dollar
    '''
    def __init__(self, url, verbose=False):
        ''' url must be a string containing the url for a single BevMo keg '''
        self.url = url

        ''' Prints contents of the object during parsing and also whether a match occurs '''
        self.verbose = verbose

        ''' Flag to prevent parsing more than once '''
        self.parsed = False

        ''' The ratio of gallons of alcohol per dollar '''
        self.ratio = None


    def open(self):
        webbrowser.open(self.url)


    def parse(self):
        ''' retrieves the page and parses the contents into the following fields

                self.name    (May include brewery/brand and/or beer)
                self.price   (USD)
                self.volume  (Gallons)
                self.num_avail  (Kegs)
                self.desc    (Keg description)
        '''
        if self.parsed:
            return

        self.parsed = True

        html = get_html(self.url)

        ''' Attempt to get name and volume '''
        try:
            self.name = html.xpath('//h1/text()')[0].strip()
            if '(' in self.name and ')' in self.name:
                    split_name = self.name.split('(')
                    self.name = split_name[0].strip()

                    volume = filter(lambda x: is_num(x) if '.' not in x else x, split_name[1].strip(')').strip())
                    if is_num(volume):
                        self.volume = float(volume)
                    else:
                        print('Failed to retrieve volume!')
                        self.volume = 0.0
            else:
                print('Failed to retrieve volume!')
                self.volume = 0.0
        except Exception as e:
            self.name = ''
            self.volume = 0.0
            
        ''' Attempt to get price '''
        try:
            self.price = float(html.xpath('//span[@class="ProductDetailItemPrice"]/text()')[0].strip().strip('$'))
        except Exception as e:
            self.price = 0.0
       
        ''' Attempt to get number of available kegs '''
        try:
            self.num_avail = int(html.xpath('//em/text()')[0].strip().split()[0])
        except Exception as e:
            self.num_avail = 0
        
        ''' Attempt to get description '''
        try:
            self.desc = html.xpath('//td[@class="ProductDetailCell"]/p/text()')[0].strip()
        except Exception as e:
            self.desc = ''


    def match(self, alc_ref):
        ''' Attempts to match keg to a beer in the alcohol reference
        
            Returns None or the alcohol % found
        '''
        matched_words = []

        if not self.parsed:
            self.parse()

        ''' If brand is matched we search for the beer with the most words matching '''
        max_matches = 0
        chosen_beer = None

        ''' alc_ref format is: {'Brewery/Brand' : {'Beer' : 'Alcohol %'}}

            alc_ref['first brand letter']['brand']['beer'] to get alcohol %
        '''
        for brand in alc_ref.iterkeys():
            ''' Every word in the brand must be in the keg name for a match '''
            matched_words = [word in self.name for word in brand.split()]
            if all(matched_words):
                ''' Find beer with most words matching, if any '''
                max_matches = 0
                chosen_beer = None
                for beer in alc_ref[brand].iterkeys():
                    matched_words = [word in self.name for word in beer.split()]
                    if any(matched_words) and len(matched_words) > max_matches:
                        max_matches = len(matched_words)
                        chosen_beer = beer 

                if max_matches > 0:
                    if self.verbose:
                        print('Matched keg {} to {} {}.'.format(self.name, brand, chosen_beer)),
                    return alc_ref[brand][chosen_beer]

        ''' If we've reached this point there is no match, so return None '''
        if self.verbose:
            print('No match for keg {}'.format(self.name))

        return None


    def get_ratio(self, alc_ref):
        ''' Matches the alcohol % and returns the volume of alcohol per USD '''
        alcohol_pct = self.match(alc_ref)
        if alcohol_pct is not None:
            ratio = (alcohol_pct * .1 * self.volume) / self.price

            if self.verbose:
                print('\tRatio: {}'.format(str(ratio)))
            self.ratio = ratio
            return ratio
        else:
            return None


