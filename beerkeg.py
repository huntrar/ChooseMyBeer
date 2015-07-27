
import re
import webbrowser
from urlparse import urlparse

from utils import get_text, get_html, is_num, unique



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


    def get_abv(self):
        ''' Attempts to find alcohol percentage using bing first result '''
        abv = ''

        ''' A ceiling for ABV content for validation
        
            We can assume BevMo does not offer kegs with this high of an alcohol content
        '''
        max_abv = 20.0
        
        if not self.parsed:
            self.parse()

        search_url = 'https://www.bing.com/search?q=' + '+'.join(self.name.split()) + '+alcohol+content'
        #search_links = filter(lambda x: 'bing.com' not in x, get_html(search_url).xpath('//a/@href'))
        search_links = get_html(search_url).xpath('//a/@href')

        '''
        print 'search links is '
        for link in search_links:
            print link
        print('')
        '''
        results = filter(lambda x: x != '#', search_links[search_links.index('javascript:'):][1:])

        ''' Search up to num_searches of the first results on bing for the alcohol content using a regex '''
        num_searches = 3

        ''' Filter links with same domain to improve chances of matching '''
        searched_domains = set()
        
        ''' Add the top page results that are unique, r_it is an iterator '''
        top_results = []
        r_it = 0
        result_link = ''

        while len(top_results) < num_searches:
            result_link = results[r_it]
            domain = '{url.netloc}'.format(url=urlparse(result_link))
            if '.' in domain:
                if domain.count('.') > 1:
                    domain = domain.split('.')[1]
                else:
                    domain = domain.split('.')[0]

            if domain in searched_domains:
                r_it += 1
            else:
                top_results.append(result_link)
                r_it += 1
                searched_domains.add(domain)

        for i in xrange(num_searches):
            try:
                search_text = ''.join(get_text(get_html(top_results[i])))
            except Exception:
                continue

            ''' Retrieves partial string containing the words ABV and a % '''
            abv = re.search('(?<=[Aa][Bb][Vv])[^\d]*(\d+[.]?\d*)(?=%)|(?<=%)[^\d]*(\d+[.]?\d*)[^\d]*(?=[Aa][Bb][Cc])', search_text)
            if abv:
                abv = abv.group()

                ''' Filters for a number with or without a decimal pt '''
                abv = float(re.search('(\d+[.]?\d*)', abv).group())

                if abv < max_abv:
                    if self.verbose:
                        print('ABV for {} is {}'.format(self.name, abv))

                    return abv
            else:
                if self.verbose:
                    print('No ABV found on {}'.format(top_results[i]))

        ''' No ABV was found by this point '''
        if self.verbose:
            print('ABV not found for {}'.format(self.name))

        return None


    def get_ratio(self):
        ''' Returns the volume of alcohol per USD '''
        alcohol_pct = self.get_abv()
        if alcohol_pct is not None:
            ratio = (alcohol_pct * .1 * self.volume) / self.price

            if self.verbose:
                print('\tRatio: {}'.format(str(ratio)))
            self.ratio = ratio
            return ratio
        else:
            return None


