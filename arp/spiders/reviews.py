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

import os

this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data", "hotel.ids")

hotel_ids = []

with open(DATA_PATH) as f:
    for line in f:
        hotel_ids.append( line.strip() )


class ReviewsSpider(CrawlSpider):
    call = 0
    name = 'reviews'
    allowed_domains = ['agoda.com']
    #start_urls = ['http://www.agoda.com/pages/agoda/popup/popup_review.aspx?hotelID=48521']
    start_urls = map( lambda x: arp.settings.REVS_URL_PATT.replace( 'HOTEL_ID', x ) , hotel_ids ) 

    def parse( self, response ):
        sel = Selector( response )
        hotel = re.search('\d+$', response.url).group(0)
        hotel_name = sel.xpath("//span[@id='ctl00_blankContent_lblHotelName']/text()").extract()
        hotel_score = sel.xpath("//span[@id='ctl00_blankContent_lblTotalScore']/text()").extract()[0]
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
                meta={'call': self.call},
                callback = self.parse )
        rets = []
        for rev in sel.xpath("//div[starts-with(@id, 'pnlReview_')]"):
            rScore = rev.xpath("//span[contains(@id, '_lblMemberScore')]/text()").extract()
            rTitle = rev.xpath("//span[contains(@id, '_lblReviewTitle')]/text()").extract()
            rLiked = rev.xpath("//span[contains(@id, '_lblProComment')]/text()").extract()
            rDetail = rev.xpath("//span[contains(@id, '_lblCommentText')]/text()").extract()
        yield ArpItem(  hotel = hotel, hotel_name = hotel_name, hotel_score = hotel_score, score = rScore, title=rTitle,
                                liked = rLiked, detail=rDetail)

