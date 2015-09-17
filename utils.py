import random
import string
import sys

import lxml.html as lh
import requests


try:
    from urllib import getproxies
except ImportError:
    from urllib.request import getproxies


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) '
               'Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) '
               'Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) '
               'Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) '
               'AppleWebKit/536.5 (KHTML, like Gecko) '
               'Chrome/19.0.1084.46 Safari/536.5',
               'Mozilla/5.0 (Windows; Windows NT 6.1) '
               'AppleWebKit/536.5 (KHTML, like Gecko) '
               'Chrome/19.0.1084.46 Safari/536.5')


def get_proxies():
    proxies = getproxies()
    filtered_proxies = {}
    for key, value in proxies.items():
        if key.startswith('http://'):
            if not value.startswith('http://'):
                filtered_proxies[key] = 'http://{0}'.format(value)
            else:
                filtered_proxies[key] = value
    return filtered_proxies


def get_html(url):
    try:
        ''' Get HTML response as an lxml.html.HtmlElement object '''
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as err:
        sys.stderr.write('Failed to retrieve {0}.\n'.format(url))
        sys.stderr.write('{0}\n'.format(str(err)))
        return None


def filter_printable(line):
    return [x for x in line if x in string.printable]


def get_text(html):
    text = html.xpath('//*[not(self::script) and not(self::style)]//text()')
    return [filter_printable(x) for x in text]


def is_num(num):
    ''' Characters to ignore when checking if value is a number '''
    ignore = ['-', '<', '>']
    try:
        for sym in ignore:
            if sym in num:
                num = num.replace(sym, '')
        new = float(num)
        return True
    except ValueError:
        return False


def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item

