# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ArpItem(Item):
    # define the fields for your item here like:
    # name = Field()
    hotel = Field()
    hotel_name = Field()
    hotel_score = Field()
    score = Field()
    title = Field()
    liked = Field()
    detail = Field()
    pass
