# Scrapy settings for arp project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'arp'
BOT_VERSION='1.0'
SPIDER_MODULES = ['arp.spiders']
NEWSPIDER_MODULE = 'arp.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'arp (+http://www.yourdomain.com)'


MAX_REVIEWS = 1000
REVS_PER_PAGE = 20
REVS_URL_PATT = 'http://www.agoda.com/pages/agoda/popup/popup_review.aspx?hotelID=HOTEL_ID'


EXPORT_FORMAT = 'jsonlines'
EXPORT_FILE = 'scraped_items.json'
EXPORT_ENCODING = 'utf8'
