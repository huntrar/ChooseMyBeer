# ChooseMyBeer

## find the keg that's right for you
ChooseMyBeer is intended to calculate the [BevMo beer kegs](http://www.bevmo.com/Shop/ProductList.aspx/Beer/Kegs/_/N-15Z1z141vn?DNID=Beer) with the highest alcohol volume per USD. The alcohol percentage for each keg is found by using the top result from bing. The user is given a menu to choose from the top kegs, accompanied by their volume in gallons, price, availability, and description. Choosing a keg will open the relevant BevMo page in your browser.

## Installation
* `git clone https://github.com/huntrar/ChooseMyBeer`
* `pip install requests lxml`

## Usage
    usage: choosemybeer.py [-h] [-a [ATTEMPTS]] [-f [FILTER [FILTER ...]]]
                           [-l [LIMIT]] [-t [TOP]] [-u [UNFILTER [UNFILTER ...]]]
    
    find the keg that's right for you
    
    optional arguments:
      -h, --help            show this help message and exit
      -a [ATTEMPTS], --attempts [ATTEMPTS]
                            number of attempts to resolve each ABV (default: 5)
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            find kegs with descriptions matching these keywords
      -l [LIMIT], --limit [LIMIT]
                            limit number of keg pages to crawl (default: 10000)
      -t [TOP], --top [TOP]
                            number of top kegs to display (default: 3)
      -u [UNFILTER [UNFILTER ...]], --unfilter [UNFILTER [UNFILTER ...]]
                            find kegs with descriptions not matching these
                            keywords



    usage: choosemybeer.py [-h] [-f [FILTER [FILTER ...]]] [-l [LIMIT]] [-t [TOP]]
                           [-u [UNFILTER [UNFILTER ...]]]

## Author
* Hunter Hammond (huntrar@gmail.com)

