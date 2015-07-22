
from collections import OrderedDict
import string

from utils import get_html, is_num, unique


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

        To fix malformed data, we can take advantage of the fact that an extra string is often equal to a string on the same line
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
    alc_ref = OrderedDict()
    while len(structured_text) > 2:
        ''' Remove entries from the head of the structured text list in order of our desired structure '''
        brand = structured_text.pop(0)
        beer = structured_text.pop(0)
        alcohol_pct = structured_text.pop(0)

        ''' If brand not already in reference dictionary, initialize an OrderedDict '''
        if brand not in alc_ref:
            alc_ref[brand] = OrderedDict()
        alc_ref[brand][beer] = alcohol_pct

    ''' Now we encapsulate our alcohol reference in another OrderedDict

        This time the key value is the first letter of the brand name

        We do this to improve lookup time while using the alcohol reference

        alc_ref['first brand letter']['brand']['beer'] to get alcohol %
    ''' 
    organized_alc_ref = OrderedDict()
    for brand in alc_ref.iterkeys():
        organized_alc_ref[brand[0]] = alc_ref[brand]

    return organized_alc_ref


def get_alc_reference():
    ''' Return an alcohol reference dictionary from realbeer.com
    
        Reference includes Brewery/Brand, Beer, and Alcohol %
    '''

    pages = []
    pages.append(get_html("http://www.realbeer.com/edu/health/calories.php"))
    pages.append(get_html("http://www.realbeer.com/edu/health/calories2.php"))

    pages_text = []
    for page in pages:
        ''' For info on XPaths, see:
                http://www.w3schools.com/xpath/xpath_syntax.asp
        '''
        pages_text += page.xpath('//table[@cellpadding="2"][2]/tr/td//text()')

    ''' Filter the data and return the proper reference dictionary '''
    return make_ref_dict(filter_ref_text(pages_text))


