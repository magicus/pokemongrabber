# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re
from subprocess import call

from scrapy.exceptions import DropItem

class FilterRecordedPipeline(object):
    # Download information file name, hidden by default
    info_file = '.pokemongrabber.json'

    # Return the value of filter_out, or the empty string if no filter exists
    def get_filter_out(self, item, spider):
        try:
            output_dir = item['output_dir']
            with open(output_dir + '/' + spider.show_info_file, 'r') as file:
                line = file.readline()
                show_item = json.loads(line)
                filter_out = show_item['filter_out']
                return filter_out
        except:
            # If the value or file does not exist, assume we should not filter out
            # and return an empty filter
            return ''

    def get_recorded_items(self, output_dir):
        # Note: This is inefficient: read and parse the whole json file
        # each time, without any caching. Should be enough for now,
        # though.
        recorded_items = []
        try:
            with open(output_dir + '/' + self.info_file, 'r') as file:
                for line in file:
                    item = json.loads(line)
                    recorded_items.append(item)
        except:
            # If the file does not exists, our list of recorded items is empty.
            pass
        return recorded_items

    def is_item_in_records(self, item, recorded_items):
        # Note: This is an inefficient linear search. Should be enough
        # for now, though.
        for i in recorded_items:
            # Consider it a match if video_id matches
            if 'video_id' in i:
              if i['video_id'] == item['video_id']:
                return True

        return False

    def process_item(self, item, spider):
        # Check if item is already recorded
        output_dir = item['output_dir']
        recorded_items = self.get_recorded_items(output_dir)
        if self.is_item_in_records(item, recorded_items):
            raise DropItem('Already recorded item, dropping S%s.E%s: %s.' % (item['season'], item['episode'], item['short_name']))

        # Otherwise, pass it on to downloaded
        return item

class DownloaderPipeline(object):

    def call_command(self, cmd_line, action_desc, item, spider):
        spider.log('Executing: ' + cmd_line)
        result_code = call(cmd_line, shell=True)
        if result_code != 0:
             raise DropItem('Failed to ' + action_desc + '. Result code: %i, command line: %r' % (result_code, cmd_line))

    def process_item(self, item, spider):
        # Extract basename
        basename = item['basename'].replace('%', '%%').replace("'", "'\"'\"'")

        # Command lines to run to download this data.

        # First, create output dir if not alreay existing
        output_dir = item['output_dir']
        mkdir_cmd_line="mkdir -p '" + output_dir + "'"
        self.call_command(mkdir_cmd_line, 'create output directory', item, spider)

        # Start by downloading video
        video_id = item['video_id']
        delve_url = "http://assets.delvenetworks.com/player/loader.swf?mediaId=" + video_id
        downloader_cmd_lines = "youtube-dl '" + delve_url + "' -o '" + output_dir + '/' + basename + ".%(ext)s'"

        self.call_command(downloader_cmd_lines, 'download video', item, spider)

        return item

class RecordDownloadedPipeline(object):
    # Download information file name, hidden by default
    info_file = '.pokemongrabber.json'
    stored_items = []

    def record_item(self, item):
        # At this point, we can be sure that the output dir is alreay existing
        self.stored_items.append(item)
        output_dir = item['output_dir']
        with open(output_dir + '/' + self.info_file, 'a') as file:
            line = json.dumps(dict(item)) + '\n'
            file.write(line)

    def process_item(self, item, spider):
        # Record that we got it now
        self.record_item(item)
        return item
