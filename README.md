# ChooseMyBeer

## find the keg that's right for you
ChooseMyBeer is intended to calculate the [BevMo beer kegs](http://www.bevmo.com/Shop/ProductList.aspx/Beer/Kegs/_/N-15Z1z141vn?DNID=Beer) with the highest alcohol volume per USD. The alcohol percentage for each keg is found by using the top result from bing. The user is given a menu to choose from the top kegs, accompanied by their volume in gallons, price, availability, and description. Choosing a keg will open the relevant BevMo page in your browser.

## Results
    Results of running ChooseMyBeer with default options as of Aug/19/2015

    0. Pabst Blue Ribbon    Ratio: 0.0734773477348
    Available: 3    Volume: 15.5 Gal.       Price: $99.99
    Pabst Blue Ribbon is a premium lager brew crafted with a hefty infusion of 6-row 
    barley in its ingredient package, a carefully balanced carbohydrate profile from 
    corn syrup, and Pacific domestic hops.

    1. Grand Teton Bitch Creek ESB  Ratio: 0.0664323675639
    Available: 4    Volume: 15.5 Gal.       Price: $174.99
    Bitch Creek perfectly balances big malt sweetness and robust hopflavor for full-
    bodied mahogany ale. Like the stream for which is named, our Bitch Creek ESB is 
    full of character..not for the timid.

    2. Full Sail Amber Ale  Ratio: 0.0608972069434
    Available: 3    Volume: 15.5 Gal.       Price: $139.99
    GOLD MEDAL 2010 BEVERAGE TESTING INSTITUTE. Deep reddish hue; medium-bodied; very 
    smoky, roasted aromas; flavors follow from the aromas with heavily smoked, burnt-malt accents.

## Installation
* `git clone https://github.com/huntrar/ChooseMyBeer`
* `pip install requests lxml`

## Usage
    usage: choosemybeer.py [-h] [-a [ATTEMPTS]] [-f [FILTER [FILTER ...]]]
                           [-l [LIMIT]] [-p [PRICE]] [-t [TOP]]
                           [-u [UNFILTER [UNFILTER ...]]]

    find the keg that's right for you

    optional arguments:
      -h, --help            show this help message and exit
      -a [ATTEMPTS], --attempts [ATTEMPTS]
                            number of attempts to resolve each ABV (default: 10)
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            find kegs with descriptions matching these keywords
      -l [LIMIT], --limit [LIMIT]
                            limit number of kegs to crawl (default: 10000)
      -p [PRICE], --price [PRICE]
                            limit the price range
      -t [TOP], --top [TOP]
                            number of top kegs to display (default: 3)
      -u [UNFILTER [UNFILTER ...]], --unfilter [UNFILTER [UNFILTER ...]]
                            find kegs with descriptions not matching these
                            keywords

## Author
* Hunter Hammond (huntrar@gmail.com)

