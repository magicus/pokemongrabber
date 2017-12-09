from scrapy.selector import Selector
from scrapy.spider import Spider

from scrapy import signals
from scrapy import log

from scrapy.signalmanager import SignalManager
from scrapy.xlib.pydispatch import dispatcher

from pokemongrabber.items import PokemongrabberItem
from pokemongrabber.pipelines import RecordDownloadedPipeline

from subprocess import check_output

class PokemongrabberSpider(Spider):
    name = 'pokemongrabber_spider'
    allowed_domains = ['pokemon.com']
    start_urls = ['https://www.pokemon.com/se/pokemon-avsnitt']

    # Accepted argument:
    #  'base' = base directory in which to create output directory based
    #           on show name.
    def __init__(self, url=None, out=None, base=None, only=None, *args, **kwargs):
        super(PokemongrabberSpider, self).__init__(*args, **kwargs)
        SignalManager(dispatcher.Any).connect(self.closed_handler, signal=signals.spider_closed)
        if base==None:
            raise Exception('Must provide argument "-a base=..."')
        self.output_base_dir = base

    def parse(self, response):
        sel = Selector(response)
        videos = sel.xpath("//ul[@class='slider']/li[@class='match']/a[@class='video']")
        items = []
        for video in videos:
            item = PokemongrabberItem()
            item['video_id'] = video.xpath("@data-video-id").extract()[0]
            item['short_name'] = video.xpath("@data-video-slug").extract()[0]
            item['title'] = video.xpath("@data-video-title").extract()[0]
            item['season'] = video.xpath("@data-video-season").extract()[0].zfill(2)
            item['episode'] = video.xpath("@data-video-episode").extract()[0].zfill(2)
            item['summary'] = video.xpath("@data-video-summary").extract()[0]

            item['basename'] = "Pokemon.S" + item['season'] + '.E' +  item['episode'] + '.' + item['title']
            item['output_dir'] = self.output_base_dir + '/Pokemon/'

            items.append(item)

        return items

    # This is called when spider is done
    def closed_handler(self, spider):
        spider.log("==== Summary of downloaded videos ====")
        for item in RecordDownloadedPipeline.stored_items:
            spider.log("Downloaded: 'S%sE%s - %s' as %s/%s" %  (item['season'], item['episode'], item['title'], item['output_dir'], item['basename']))
