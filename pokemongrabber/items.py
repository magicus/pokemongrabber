# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class PokemongrabberItem(Item):
    # define the fields for your item here like:
    # name = Field()
    video_id = Field()
    short_name = Field()
    title = Field()
    season = Field()
    episode = Field()
    summary = Field()
    basename = Field()
    output_dir = Field()
