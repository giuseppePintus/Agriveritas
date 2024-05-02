# Scrapy settings for attemp3 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "attemp3"

SPIDER_MODULES = ["attemp3.spiders"]
NEWSPIDER_MODULE = "attemp3.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "attemp3 (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "attemp3.middlewares.Attemp3SpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "attemp3.middlewares.Attemp3DownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "attemp3.pipeDownload.PipeDownload": 200,
   # "attemp3.pipelines.Attemp3Pipeline": 300,
    "attemp3.pipeJinaRequest.JinaRequest": 201,
    "attemp3.pipeJPParser.JPParser": 202,
    # "attemp3.pipeJPParser2.JPParser2": 203,
    "attemp3.pipeCsvResults.CsvPipeline" : 900,
    
    "attemp3.pipeMilvus.PipeMilvus": 945,

    "attemp3.pipeJsonResults.JsonPipeline" : 955,
}

FILES_STORE = "download"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"






# Enable logging
LOG_LEVEL = "DEBUG"  # Set to "INFO" or "WARNING" if you want less verbosity

# Set the log file and log format
LOG_FILE = "scrapy.log"
LOG_FORMAT = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"

# Enable or disable HTTP compression
HTTP_COMPRESSION_ENABLED = True
HTTP_COMPRESSION_ALGORITHMS = ["gzip", "deflate"]

# Set the user agent rotation strategy
USER_AGENT_ROTATION_ENABLED = True
USER_AGENT_ROTATION_STRATEGY = "random"  # or "custom" if you have a custom rotation list

# # Set the maximum depth of crawling
# DEPTH_LIMIT = 2

# # Set the maximum number of pages to be scraped
MAX_PAGES_TO_CRAWL = 1

# Set the maximum number of concurrent requests
CONCURRENT_REQUESTS = 32

# Set the maximum number of concurrent requests per domain
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Set the maximum number of concurrent requests per IP
CONCURRENT_REQUESTS_PER_IP = 2

# # Set the download delay between requests
# DOWNLOAD_DELAY = 2

# # Set the retry delay for failed requests
# RETRY_DELAY = 5

# Set the retry requests for failed requests
RETRY_TIMES = 3

# Set the custom user agent
CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

# Set the custom headers
CUSTOM_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf"#q=0.9,*/*;q=0.8",
   #  "Accept-Language": "en-US,en;q=0.5",
}