import hashlib
from pathlib import Path
import scrapy
from scrapy.utils.project import get_project_settings
import time
from scrapy.selector import Selector
from urllib.parse import urlparse


class ERSpired(scrapy.Spider):
    name = 'scraperER'
    
    start_urls = [
        "https://agrea.regione.emilia-romagna.it/",
        # "https://agrea.regione.emilia-romagna.it/agenzia/allegati-agenzia/certificate-signed.pdf/@@download/file/certificate-signed.pdf"

        #"https://agreagestione.regione.emilia-romagna.it/opendocument/normativa/download-file?id=13262&version=1"
        # "https://agrea.regione.emilia-romagna.it/agenzia/sicurezza-delle-informazioni/allegati-sicurezza-delle-informazioni/pl_01_politica-della-sicurezza-delle-informazioni_8.pdf/@@download/file/PL_01_Politica%20della%20sicurezza%20delle%20informazioni_8.pdf",
        # "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/AdapterHTTP?action_name=ACTIONRICERCADELIBERE&operation=downloadTesto&codProtocollo=DAG/2023/1482&ENTE=2"
        #"https://quotes.toscrape.com/page/1/",
    ]

    allowed_domains = ['agrea.regione.emilia-romagna.it']

    logFile = "myLogSpider.txt"
    pdLogFile = ""
    saveDir = ""

    visited = set()  # Set to keep track of visited URLs
    # counter = 0  # Counter for downloaded pages
    # amountToCrawl = -1


    def log(self, toLog="", aCapo=0):
        print(("\n" * aCapo) + toLog)
        with open(self.logFile, "a") as f:
            f.write(("\n" * aCapo) + toLog + "\n")

    def JPnormalizeUrl(self, url):
        toRet = url
        lastC = str(url)[-1]
        finishUrls = ['/', '//', '\\']
        if lastC in finishUrls: # and len(url.split("/")[-1].split(".")) == 1:
            toRet = url[:-1]
        return toRet
    
        # lastC = str(url)[-1]
        # finishUrls = ['/', '//', '\\']
        # self.log("@@ -> " + url + "   " + str(len(url.split("."))))
        # if not lastC in finishUrls and len(url.split("/")[-1].split(".")) == 1:
        #     url += '/'
        
        # return url

    def pushUrl(self, url):
        self.visited.add(url)

    def parse(self, response):

        # Compute the hash code of the response body
        hash_code = hashlib.sha256(response.body).hexdigest()

        requiredMainTableInfo = {
            "IDres" : hash_code,
            "IDregion" : "ER",
            "urlFrom" : response.url, #"sito web provenienza": "",
            "HTTPStatus" : response.status,
            "fileDownloadedName": "",
            "fileDownloadedDir": "",
            "timestampDownload" : time.time(),
            "timestampUpload" : "",
            
            "aborted" : False,
            "abortReason": ""
        }
        

        item = {
            "response": response,
            "tableRow" : requiredMainTableInfo,
            "domains" : self.allowed_domains
        }

        # # Modify the <a> tags in the downloaded file
        # if response.headers.get('Content-Type', b'').startswith(b'text/html'):
        #     modified_body = self.modify_a_tags(response)
        #     item['response'] = response.replace(body=modified_body)

        self.log("NUOVO FILE")
        if str(response.url).endswith(".html"):
            self.log("ooooooooo " + str(response.url))
            
        self.log(str(item))
        self.log(str(response))
        self.log("")


        
        yield item

        # Extract links and follow them if not visited before
        # Check if the response content is in text format
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):

#            if urlparse(response.url).netloc == self.allowed_domains[0]:
            links = response.css('a::attr(href)').getall()
            for link in links:
                tmpurl = response.urljoin(link)
                absolute_url = self.JPnormalizeUrl(tmpurl)
                parsed_url = urlparse(absolute_url)
                self.log("°°°°°°°°°°°°°°°°")
                self.log(str(link))
                self.log(str(absolute_url))
                self.log(str(parsed_url))
                self.log(str(parsed_url.netloc))
                self.log("°°°°°°°°°°°°°°°°", aCapo=2)
                #if absolute_url not in self.visited:
                if parsed_url.netloc == self.allowed_domains[0] and absolute_url not in self.visited:
                    self.pushUrl(absolute_url)
                    yield scrapy.Request(absolute_url, callback=self.parse)


        #yield self.crawlingRule1(response=response)
        # # Increment the counter
        # self.counter += 1

        # # # Check if the counter reaches 10
        # # if self.counter >= self.amountToCrawl:
        # #     return

        # # Extract links and follow them if not visited before
        # links = response.css('a::attr(href)').getall()
        # for link in links:
        #     # self.log(link)
        #     # self.log(response.url)
        #     absolute_url = response.urljoin(link)
        #     # self.log(absolute_url)
        #     # self.log(aCapo=3)
        #     if absolute_url not in self.visited:
        #         self.visited.add(absolute_url)
        #         yield scrapy.Request(absolute_url, callback=self.parse)     

    def crawlingRule1(self, response):
        # Extract links and follow them if not visited before
        # Check if the response content is in text format
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):

#            if urlparse(response.url).netloc == self.allowed_domains[0]:
            links = response.css('a::attr(href)').getall()
            for link in links:
                tmpurl = response.urljoin(link)
                absolute_url = self.JPnormalizeUrl(tmpurl)
                parsed_url = urlparse(absolute_url)
                self.log("°°°°°°°°°°°°°°°°")
                self.log(str(link))
                self.log(str(absolute_url))
                self.log(str(parsed_url))
                self.log(str(parsed_url.netloc))
                self.log("°°°°°°°°°°°°°°°°", aCapo=2)
                #if absolute_url not in self.visited:
                if parsed_url.netloc == self.allowed_domains[0] and absolute_url not in self.visited:
                    self.pushUrl(absolute_url)
                    yield scrapy.Request(absolute_url, callback=self.parse)

    def crawlingRule2(self, response):
        # Extract links and follow them if not visited before
        # Check if the response content is in text format
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):

            if urlparse(response.url).netloc == self.allowed_domains[0]:
                links = response.css('a::attr(href)').getall()
                for link in links:
                    tmpurl = response.urljoin(link)
                    absolute_url = self.JPnormalizeUrl(tmpurl)
                    parsed_url = urlparse(absolute_url)
                    self.log("°°°°°°°°°°°°°°°°")
                    self.log(str(link))
                    self.log(str(absolute_url))
                    self.log(str(parsed_url))
                    self.log(str(parsed_url.netloc))
                    self.log("°°°°°°°°°°°°°°°°", aCapo=2)
                    if absolute_url not in self.visited:
                    #if parsed_url.netloc == self.allowed_domains[0] and absolute_url not in self.visited:
                        self.pushUrl(absolute_url)
                        yield scrapy.Request(absolute_url, callback=self.parse)

    # def modify_a_tags(self, response):
    #     # Create a Selector from the response body
    #     selector = Selector(text=response.body.decode())

    #     # Modify the <a> tags as needed
    #     a_tags = selector.css('a')
    #     for a_tag in a_tags:
    #         # Modify the href attribute or any other properties
    #         href = a_tag.attrib['href']
    #         if href.startswith('http'):
    #             local_reference = '#' + href.split('#')[-1]
    #             modified_href = response.urljoin(local_reference)
    #             a_tag.attrib['href'] = modified_href

    #     # Get the modified HTML body
    #     modified_body = selector.get()

    #     return modified_body.encode()






























# import hashlib
# from pathlib import Path
# import scrapy
# from scrapy.utils.project import get_project_settings
# import time
# from scrapy.selector import Selector

# class Try1Spider(scrapy.Spider):
#     name = 'try'
#     # allowed_domains = ['example.com']
#     # start_urls = [
#     #     'https://quotes.toscrape.com/page/1/'
#     #     ]

#     # def parse(self, response):
#     #     # Extract the page content and save it as a file
#     #     page_content = response.body
#     #     filename = response.url.split("/")[-1] + '.html'
#     #     with open(filename, 'wb') as f:
#     #         f.write(page_content)
#     #     self.log('Saved file %s' % filename)
#     start_urls = [
#         "https://agrea.regione.emilia-romagna.it/",
#         # "https://agrea.regione.emilia-romagna.it/agenzia/allegati-agenzia/certificate-signed.pdf/@@download/file/certificate-signed.pdf"

#         #"https://agreagestione.regione.emilia-romagna.it/opendocument/normativa/download-file?id=13262&version=1"
#         # "https://agrea.regione.emilia-romagna.it/agenzia/sicurezza-delle-informazioni/allegati-sicurezza-delle-informazioni/pl_01_politica-della-sicurezza-delle-informazioni_8.pdf/@@download/file/PL_01_Politica%20della%20sicurezza%20delle%20informazioni_8.pdf",
#         # "https://servizissiir.regione.emilia-romagna.it/deliberegiunta/servlet/AdapterHTTP?action_name=ACTIONRICERCADELIBERE&operation=downloadTesto&codProtocollo=DAG/2023/1482&ENTE=2"
#         #"https://quotes.toscrape.com/page/1/",
#     ]

#     logFile = "myLogSpider.txt"
#     pdLogFile = ""
#     saveDir = ""

#     visited = set()  # Set to keep track of visited URLs
#     counter = 0  # Counter for downloaded pages
#     amountToCrawl = -1


#     def log(self, toLog="", aCapo=0):
#         print(("\n" * aCapo) + toLog)
#         with open(self.logFile, "a") as f:
#             f.write(("\n" * aCapo) + toLog + "\n")


#     def parse(self, response):

#         # Compute the hash code of the response body
#         hash_code = hashlib.sha256(response.body).hexdigest()

#         requiredMainTableInfo = {
#             "IDres" : hash_code,
#             "urlFrom" : response.url,
#             #"sito web provenienza": "",
#             "HTTPStatus" : response.status,
#             "fileDownloadedName": "",
#             "fileDownloadedDir": "",
#             "timestampDownload" : time.time(),
#             "timestampUpload" : "",
#         }


#         item = {
#             "response": response,
#             "tableRow" : requiredMainTableInfo 
#         }

#         # Modify the <a> tags in the downloaded file
#         if response.headers.get('Content-Type', b'').startswith(b'text/html'):
#             modified_body = self.modify_a_tags(response)
#             item['response'] = response.replace(body=modified_body)

#         self.log("NUOVO FILE")
#         self.log(str(item))
#         self.log(str(response))
#         self.log("")

#         yield item

#         # Increment the counter
#         self.counter += 1

#         # # Check if the counter reaches 10
#         # if self.counter >= self.amountToCrawl:
#         #     return

#         # Extract links and follow them if not visited before
#         links = response.css('a::attr(href)').getall()
#         for link in links:
#             # self.log(link)
#             # self.log(response.url)
#             absolute_url = response.urljoin(link)
#             # self.log(absolute_url)
#             # self.log(aCapo=3)
#             if absolute_url not in self.visited:
#                 self.visited.add(absolute_url)
#                 yield scrapy.Request(absolute_url, callback=self.parse)
#         #page = response.url.split("/")[-2]
#         #filename = f"quotes-{page}.html"
#         #Path(filename).write_bytes(response.body)
    
#     def modify_a_tags(self, response):
#         # Create a Selector from the response body
#         selector = Selector(text=response.body.decode())

#         # Modify the <a> tags as needed
#         a_tags = selector.css('a')
#         for a_tag in a_tags:
#             # Modify the href attribute or any other properties
#             href = a_tag.attrib['href']
#             if href.startswith('http'):
#                 local_reference = '#' + href.split('#')[-1]
#                 modified_href = response.urljoin(local_reference)
#                 a_tag.attrib['href'] = modified_href

#         # Get the modified HTML body
#         modified_body = selector.get()

#         return modified_body.encode()