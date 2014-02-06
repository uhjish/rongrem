from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from arp.items import ArpItem
from scrapy.http import FormRequest
from scrapy.http import Request

import arp.settings
import math
import re
import sys


class ReviewsSpider(CrawlSpider):
    call = 0
    name = 'reviews'
    allowed_domains = ['agoda.com']
    #start_urls = ['http://www.agoda.com/pages/agoda/popup/popup_review.aspx?hotelID=48521']
    start_urls = ['http://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=K6u3PM57cnhUEInlew7CtH01GFt7GE%2b3x4mJqeNW%2bQL7sa8UJ6lbKBrbda6LYxoiINpTYHscXuS70Smj2dcYKTf3nVW9cwcsXQudyVKZy6BeB5DzshsPD6M0pe3tToZdzSIpDA898q%2f7f6rrRIqdP7%2fqq1B4EXYj91Qi%2fruY5f8pzOI7c4OY%2bSLPBiSynLnncefoQV35wWwPJxhsVh90ctTURA31RA%2bUg%2bDFMU7joKG4TsoE%2f5BXTr%2b2WbTKrnTIW6v%2b1z7ngi%2fh%2bcIMzh%2fx3w%3d%3d&tick=635272808406']
    '''rules = (
        Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )
    '''
    def parse( self, response):
        sel = Selector( response )
        hotelsHdr = sel.xpath("string(//p[@id='pHeadertext'])").extract()[0]
        print "hotels: ", hotelsHdr.encode('unicode-escape')
        m = re.search('found (\d+) hotels', hotelsHdr)
        hotelsCnt = int(m.group(1))
        m = re.search('\d+\s*$', hotelsHdr)
        hotelLast=int(m.group(0).strip())
        print "hot: ", hotelLast
        viewState = sel.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        #print viewState
        #sys.exit(0)
        try:
            lastCall = response.request.meta['call']
        except:
            lastCall = 0
        print "lastCall: ", lastCall
        self.call += 1
        if hotelsCnt > hotelLast:
            yield FormRequest.from_response(
                response,
                formdata={'__EVENTTARGET': 'ctl00$ContentMain$lbtnFooterNext',
                          '__EVENTARGUMENT': '',
                          'ctl00$scriptmanager1':'ctl00$ContentMain$upResultFooter|ctl00$ContentMain$lbtnFooterNext',
                          '__VIEWSTATE': viewState
                          },
                cookies = [{'name':'firstssrlanding', 'value':'false',
                            'domain':'www.agoda.com', 'path':'/pages/agoda/default'}],
                dont_click=True,
                dont_filter=True,
                meta={'call': self.call},
                callback = self.parse )
        '''for rev in sel.xpath("//a[starts-with(@id, 'lnkPopupReview')]/@id"):
            hotId = rev.extract().replace("lnkPopupReview","")
            hotRevs = arp.settings.REVS_URL_PATT.replace('HOTEL_ID', hotId)
            yield Request( url=hotRevs, callback=self.parse_reviews, meta={'hotel': hotId})
'''
    def parse_reviews( self, response ):
        sel = Selector( response )
        hotel = response.meta['hotel']
        totalReviews = int(sel.xpath("//input[@id='hidTotalReviews']/@value").extract()[0])
        curPage = int(sel.xpath("//input[@id='hidCurrentPage']/@value").extract()[0])
        maxPage = min(  math.floor(arp.settings.MAX_REVIEWS / arp.settings.REVS_PER_PAGE), 
                        math.floor(totalReviews / arp.settings.REVS_PER_PAGE) )
        viewState = sel.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        print "total Reviews: ", totalReviews, curPage, maxPage
        if curPage < maxPage:
            yield FormRequest.from_response(
                response,
                formdata={'__EVENTTARGET': 'ctl00$blankContent$btnNextPage',
                          '__EVENTARGUMENT': '',
                          '__VIEWSTATE': viewState
                          },
                dont_click=True,
                dont_filter=True,
                meta={'call': self.call, 'hotel': hotel},
                callback = self.parse_reviews )
        rets = []
        for rev in sel.xpath("//div[starts-with(@id, 'pnlReview_')]"):
            rScore = rev.xpath("//span[contains(@id, '_lblMemberScore')]/text()").extract()
            rTitle = rev.xpath("//span[contains(@id, '_lblReviewTitle')]/text()").extract()
            rLiked = rev.xpath("//span[contains(@id, '_lblProComment')]/text()").extract()
            rDetail = rev.xpath("//span[contains(@id, '_lblCommentText')]/text()").extract()
        yield ArpItem(  hotel = hotel, score = rScore, title=rTitle,
                                liked = rLiked, detail=rDetail)

