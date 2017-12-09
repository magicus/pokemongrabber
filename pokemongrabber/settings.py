# Scrapy settings for pokemongrabber project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'pokemongrabber'

SPIDER_MODULES = ['pokemongrabber.spiders']
NEWSPIDER_MODULE = 'pokemongrabber.spiders'

ITEM_PIPELINES = {
    'pokemongrabber.pipelines.FilterRecordedPipeline':   200,
    'pokemongrabber.pipelines.DownloaderPipeline':       800,
    'pokemongrabber.pipelines.RecordDownloadedPipeline': 900,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'pokemongrabber (+http://www.yourdomain.com)'
