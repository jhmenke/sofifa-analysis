import scrapy

class QuotesSpider(scrapy.Spider):
    name = "sofifa"

    start_urls = [f'https://sofifa.com/?offset={offset}' for offset in range(0, 20000, 60)]


    def parse(self, response):
        """parse the list of players on each page in start_urls, collect links to each player profile"""

        #for each link on the page
        for link in response.xpath('//a/@href').extract():
            
            #if the link contains "player/" and is not present in the 'links_collected.txt' file, then follow the link
            if 'player/' in link and link not in open('links_collected.txt').read():
                # link += "&hl=en-US&layout=old" if "?" in link else "?hl=en-US&layout=old"
                yield response.follow(link, self.parse_player)


    def parse_player(self, response):
        """parse the player profile page and collect various attributes and identifiers"""
        data = {
            'link': response.url,
            'short_name': response.xpath('//h1/text()')[0].get(),
            'name': response.xpath('//h1/text()')[1].get().split("(")[0].strip(),
            'country': response.xpath('//div[contains(@class,"meta bp3-text-overflow-ellip")]/a/@title').get(),
            'country_link': response.xpath('//div[contains(@class,"meta bp3-text-overflow-ellip")]/a/@href').get(),
            'age': response.xpath('//div[contains(@class,"meta bp3-text-overflow-ellip")]/text()')[-1].get().split("y.o.")[0].strip()
        }

        #--------------------
        # COLLECT NAME, COUNTRY, AGE
        #--------------------

        #--------------------
        # COLLECT OVERAL RATINGS
        #--------------------
        overall_stats =  response.xpath('//div[contains(@class,"column col-3")]/div')
        data['overall_rating'] = overall_stats[0].xpath("span/text()").get()
        data['potential'] = overall_stats[1].xpath("span/text()").get()
        data['value'] = overall_stats[2].xpath("text()").get()
        data['wage'] = overall_stats[3].xpath("text()").get()
        data['position'] = response.xpath('//div[contains(@class, "player-card double-spacing")]/*/li/span[contains(@class, "pos")]/text()').get()

        #--------------------
        # COLLECT POPULARITY METRICS
        #--------------------
        popularity = response.xpath('//div/button[contains(@class, "bp3-button")]/span[contains(@class, "count")]/text()').extract()
        data['likes'] = popularity[0]
        data['dislikes'] = popularity[1]
        data['followers'] = popularity[2]

        #---------------------
        # COLLECT ATTRIBUTES
        #---------------------
        ATTRIBUTES=['Crossing', 'Finishing', 'Heading Accuracy', 'Short Passing', 'Volleys',
                    'Dribbling', 'Curve', 'FK Accuracy', 'Long Passing', 'Ball Control',
                    'Acceleration', 'Sprint Speed', 'Agility', 'Reactions', 'Balance',
                    'Shot Power', 'Jumping', 'Stamina', 'Strength', 'Long Shots',
                    'Aggression', 'Interceptions', 'Positioning', 'Vision', 'Penalties', 'Composure',
                    'Defensive Awareness', 'Standing Tackle', 'Sliding Tackle',
                    'GK Diving', 'GK Handling', 'GK Kicking', 'GK Positioning', 'GK Reflexes']

        # collect the player attributes - note that we only want the last len(ATTRIBUTES) instances from the xpath result
        attrs = response.xpath('//li/span[contains(@class,"bp3-tag")]/text()').extract()[-len(ATTRIBUTES)-1:-1]
        assert len(attrs) == len(ATTRIBUTES), attrs
        for index, attr in enumerate(attrs):
            data[ATTRIBUTES[index]]=attr
        yield data
