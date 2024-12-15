import scrapy
import json
from bs4 import BeautifulSoup
import os
from datetime import datetime
import logging

class GeneralSpider(scrapy.Spider):
    name = "general"
    
    def __init__(self, config_file=None, site=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.setLevel(logging.DEBUG)
        
        if not config_file:
            raise ValueError("config_file is required")
        
        self.config = self._load_config(config_file)
        if not site or site not in self.config["sites"]:
            raise ValueError(f"Site {site} not found in config")
            
        self.site = site
        self.site_config = self.config["sites"][site]
        self.settings = self.config.get("settings", {})
        
        # Validate required settings
        if not self.settings.get("chunk_size"):
            self.logger.warning("chunk_size not specified in settings, using default: 1000")
            self.settings["chunk_size"] = 1000
        
        if not self.settings.get("chunk_overlap"):
            self.logger.warning("chunk_overlap not specified in settings, using default: 200")
            self.settings["chunk_overlap"] = 200
        
        self.start_urls = self.site_config["start_urls"]
        self.allowed_domains = self.site_config["allowed_domains"]
        
        self.logger.info(f"Spider configured with start_urls: {self.start_urls}")
        self.logger.info(f"Spider configured with allowed_domains: {self.allowed_domains}")
            
    def _load_config(self, config_file):
        self.logger.info(f"Loading config from: {config_file}")
        try:
            with open(config_file) as f:
                config = json.load(f)
                self.logger.debug(f"Loaded config: {config}")
                return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            raise
            
    def parse(self, response):
        self.logger.info(f"Parsing URL: {response.url}")
        
        # Extract content
        soup = BeautifulSoup(response.body, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        self.logger.debug(f"Extracted text length: {len(text)}")
        
        # Create chunks
        chunks = self._create_chunks(text)
        self.logger.info(f"Created {len(chunks)} chunks from URL: {response.url}")
        
        # Save chunks
        for i, chunk in enumerate(chunks):
            self._save_chunk(chunk, response.url, i)
            
        # Follow links within allowed domains
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):
            links = response.css('a::attr(href)').getall()
            self.logger.info(f"Found {len(links)} links to follow")
            for link in links:
                self.logger.debug(f"Following link: {link}")
                yield response.follow(link, self.parse)
                
    def _create_chunks(self, text):
        # Get chunk size with default value if not in settings
        chunk_size = self.settings.get("chunk_size", 1000)  # Default 1000 if not specified
        overlap = self.settings.get("chunk_overlap", 200)   # Default 200 if not specified
        
        self.logger.debug(f"Creating chunks with size: {chunk_size} and overlap: {overlap}")
        
        chunks = []
        if not text:
            self.logger.warning("Empty text received for chunking")
            return chunks
            
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            self.logger.debug(f"Created chunk {len(chunks)} with length {len(chunk)}")
            start = end - overlap
            
        return chunks
        
    def _save_chunk(self, chunk, url, index):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"/crawler/output/{self.site}/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        metadata = {
            "url": url,
            "site": self.site,
            "chunk_index": index,
            "timestamp": timestamp
        }
        
        filename = f"{output_dir}/chunk_{index}.txt"
        with open(filename, 'w') as f:
            f.write(json.dumps(metadata) + "\n---\n" + chunk)