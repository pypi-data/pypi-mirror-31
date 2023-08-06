# -*- coding: utf-8 -*-

# !!! # Crawl responsibly by identifying yourself (and your website/e-mail) on the user-agent
USER_AGENT = 'hufeallu@hotmail.com'

# settings for spiders
BOT_NAME = 'tweetscraper'
LOG_LEVEL = 'INFO'
DOWNLOAD_HANDLERS = {'s3': None,} # from http://stackoverflow.com/a/31233576/2297751, TODO

SPIDER_MODULES = ['tweetscraper.spiders']
NEWSPIDER_MODULE = 'tweetscraper.spiders'
ITEM_PIPELINES = {
    'tweetscraper.pipelines.SaveToFilePipeline':100,
    #'TweetScraper.pipelines.SaveToMongoPipeline':100, # replace `SaveToFilePipeline` with this to use MongoDB
}

# settings for where to save data on disk
SAVE_TWEET_PATH = './Data/tweet/'
SAVE_USER_PATH = './Data/user/'

# settings for mongodb
MONGODB_SERVER = "10.2.78.38"
MONGODB_PORT = 27017
MONGODB_DB = "tweetest2"        # database name to save the crawled data
MONGODB_TWEET_COLLECTION = "tweet" # collection name to save tweets
MONGODB_USER_COLLECTION = "user"   # collection name to save users


