import random
import string
import sys

import lxml.html as lh
import requests


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


def filter_printable(line):
    return filter(lambda x: x in string.printable, line)


def get_text(html):
    text = html.xpath('//*[not(self::script) and not(self::style)]//text()')
    return map(filter_printable, text)


def is_num(num):
    ''' Characters to ignore when checking if value is a number '''
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

