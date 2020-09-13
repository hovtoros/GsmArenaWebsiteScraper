import scrapy
from scrapy.crawler import CrawlerProcess

class DeviceModelsScraper(scrapy.Spider):
    name = 'DeviceModelsBot'
    start_urls = ['https://www.gsmarena.com/']

    def parse(self, response):
        brands_list_page = response.css('div[id="instores-container"] ~ h2.section > a')
        yield from response.follow_all(brands_list_page, self.parse_brands_list)

    def parse_brands_list(self, response):
        brand_pages = response.css('div.general-menu a')
        yield from response.follow_all(brand_pages, self.parse_brand_page)

    def parse_brand_page(self, response):
        device_pages = response.css('div.general-menu a')
        yield from response.follow_all(device_pages, self.parse_device)

        pagination_links = response.css('a.left ~ a')
        yield from response.follow_all(pagination_links, self.parse_brand_page)

    def parse_device(self, response):
        brand = response.css('h1.nobor::text').re(r'^\S*')
        model = response.css('h1.nobor::text').re(r'\s(.*)')
        release_year = response.css('td[data-spec="year"]::text').re_first(r'\d{4}')
        release_month = response.css('td[data-spec="year"]::text').re_first(r'\d{4}.{0,2}([a-zA-Z]{3,})')
        website_views = response.css("span[id='popularity-vote']::text").re(r'\d+,*\d+')
        website_likes = response.css("span[id='fan-vote'] strong::text").extract()
        display_size = response.css('span[data-spec="displaysize-hl"]::text').re_first(r'\d{1,2}.\d*')
        display_pixel_width = response.css('td[data-spec="displayresolution"]::text').re(r'(\d+)\s?[x]')
        display_pixel_height = response.css('td[data-spec="displayresolution"]::text').re(r'[x]\s?(\d+)')
        camera_megapixels = response.css('td[data-spec="cam1modules"]::text').re(r'^\d+')
        video_pixels = response.css('span[data-spec="videopixels-hl"]::text').extract()
        memory_gb_size = response.css('td[data-spec="internalmemory"]::text').re(r'^\d+[MBGK]{2}')
        ram_gb_size = response.css('td[data-spec="internalmemory"]::text').re_first(r'(\d+[MBGK]{2})\s*RAM')
        battery_mah_size = response.css('span[data-spec="batsize-hl"]::text').extract()
        network_types = response.css('td[data-spec="nettech"]::text').extract()
        dimension_height = response.css('td[data-spec="dimensions"]::text').re(r'^\S*')
        dimension_width = response.css('td[data-spec="dimensions"]::text').re(r'x\s(\d+.?\d)\sx')
        dimension_thickness = response.css('td[data-spec="dimensions"]::text').re(r'x\s(\d+.?\d)\sm')
        os = response.css('td[data-spec="os"]::text').extract()
        chipset = response.css('td[data-spec="chipset"]::text').extract()
        cpu = response.css('td[data-spec="cpu"]::text').extract()
        gpu = response.css('td[data-spec="gpu"]::text').extract()
        memory_slot = response.css('td[data-spec="memoryslot"]::text').re(r'^\w+')
        loudspeaker = response.xpath(
            "//table[9]//tbody[1]//tr[2]//td[2]/text()").re(r'^\w+')
        audiojack = response.xpath("//a[text()[contains(.,'3.5mm jack')]]/parent::td/following-sibling::td/text()").re(
            r'^\w+')
        wifi = response.css('td[data-spec="wlan"]::text').re(r'^\w+-?\w+')
        bluetooth = response.css('td[data-spec="bluetooth"]::text').re(r'^\S{0,3}')
        gps = response.css('td[data-spec="gps"]::text').re(r'^([\w\-]+)')
        radio = response.css('td[data-spec="radio"]::text').re(r'^\w+')
        price = response.css('td[data-spec="price"]::text').re_first(r'\d+\.?')

        yield {
            'brand': brand,
            'model': model,
            'release_year': release_year,
            'release_month': release_month,
            'website_views': website_views,
            'website_likes': website_likes,
            'display_size': display_size,
            'display_pixel_width': display_pixel_width,
            'display_pixel_height': display_pixel_height,
            'camera_megapixels': camera_megapixels,
            'video_pixels': video_pixels,
            'memory_gb_size': memory_gb_size,
            'ram_gb_size': ram_gb_size,
            'battery_mah_size': battery_mah_size,
            'network_types': network_types,
            'dimension_height': dimension_height,
            'dimension_width': dimension_width,
            'dimension_thickness': dimension_thickness,
            'os': os,
            'chipset': chipset,
            'cpu': cpu,
            'gpu': gpu,
            'memory_slot': memory_slot,
            'loudspeaker': loudspeaker,
            'audiojack': audiojack,
            'wifi': wifi,
            'bluetooth': bluetooth,
            'gps': gps,
            'radio': radio,
            'price': price
        }


process = CrawlerProcess(settings={
    "FEEDS": {
        "devices.csv": {"format": "csv"},
    },
    "USER_AGENT": 'DeviceModelsScraper',
    "ROBOTSTXT_OBEY": True,
    "CONCURRENT_REQUESTS": 8,
    "DOWNLOAD_DELAY": 0.5,
    "RANDOMIZE_DOWNLOAD_DELAY": True
})
scraper = DeviceModelsScraper()
process.crawl(DeviceModelsScraper)
process.start()