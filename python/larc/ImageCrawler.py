#coding=utf-8
__author__ = 'bchang'
import lxml
import requests
import time
from lxml import etree

class ImageCrawler:
    """ required libraries:  requests-2.7.0, lxml-3.4.4 """

    domains = {}

    def extractForTwitter(self, htmlDom):
        """twitter.com"""
        imgURL = ""
        # twitter: single image
        nodes = htmlDom.xpath(u'//div[@class="cards-base cards-multimedia"]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        else:
            # twitter: multiple images
            nodes = htmlDom.xpath(u'//div[@class="cards-base cards-multimedia"]//div[@data-resolved-url-large]')
            if len(nodes) > 0:
                imgURL = nodes[1].attrib['data-url']
        return imgURL

    def extractForWattpad(self, htmlDom):
        """ www.wattpad.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="cover cover-lg"]/img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForChannelNewsAsia(self, htmlDom):
        """ www.channelnewsasia.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@id="photo-tab"]//div[@class="main-slide"]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForVine(self, htmlDom):
        """ vine.co """
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    def extractForImgur(self, htmlDom):
        """ i.imgur.com and imgur.com"""
        #(u'i.imgur.com', 6)
        #(u'imgur.com', 4)

        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="image textbox"]/img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForNea(self, htmlDom):
        """ www.nea.gov.sg """
        imgURL = "http://www.nea.gov.sg/Html/Nea/images/common/logo.jpg"
        return imgURL

    def extractForAllkpop(self, htmlDom):
        """ www.allkpop.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="row-fluid category5"]//section[@class="post "]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForDaumcdn(self, htmlDom):
        """ t1.daumcdn.net """
        imgURL = ""
        return imgURL

    def extractForInstagram(self, htmlDom):
        """ instagram.com """
        #(u'i.instagram.com', 1)
        #(u'instagram.com', 3)
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    def extractForStaticflickr(self, htmlDom):
        """ staticflickr.com """
        #(u'farm1.staticflickr.com', 3)
        #(u'farm6.staticflickr.com', 1)
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    def crawl(self, url):
        """ get the img-url from a web page. """
        imgURL = ""
        try:
            r = requests.get(url)
            #print url, r.url
            paths = r.url.split("/")
            domain_current = paths[2]
            self.domains[domain_current] = self.domains.get(domain_current, 0) + 1
            if r.url.endswith((".jpg",'.png','.gif','.jpeg')):
                imgURL = r.url
            else:
                htmlDom = etree.HTML(r.content.decode('utf-8'))
            if imgURL == "":
                imgURL = self.extractForTwitter(htmlDom)
            if imgURL == "":
                imgURL = self.extractForWattpad(htmlDom)
            if imgURL == "":
                imgURL = self.extractForChannelNewsAsia(htmlDom)
            if imgURL == "":
                imgURL = self.extractForVine(htmlDom)
            if imgURL == "":
                imgURL = self.extractForImgur(htmlDom)
            if imgURL == "" and "nea.gov" in paths[2]:
                imgURL = self.extractForNea(htmlDom)
            if imgURL == "":
                imgURL = self.extractForAllkpop(htmlDom)
            if imgURL == "":
                imgURL = self.extractForDaumcdn(htmlDom)
            if imgURL == "":
                imgURL = self.extractForInstagram(htmlDom)
            if imgURL == "":
                imgURL = self.extractForStaticflickr(htmlDom)
            if imgURL != "" and "http://" not in imgURL and "https://" not in imgURL:
                imgURL = paths[0] + "/" + paths[1] + "/" + paths[2] + "/" + imgURL
        except Exception as e:
            print e
        return imgURL

if __name__ == '__main__':
    file = open("img-urls.txt","r")
    imgs = file.read()
    urls = imgs.split("\n")
    urls = ('http://t.co/YpKa8mu4ZD','http://t.co/O310hcutb0','http://t.co/4VVugH6PPH','http://t.co/1F44cNBKAM', 'http://t.co/FrzbHQOeT2','http://t.co/nXj392xAih','http://t.co/cNEUg6CMp4','http://t.co/TcG1uJbrpg', 'http://t.co/zpAD','http://t.co/5FnLm00Eja','http://t.co/rKqvvf0mPp','https://t.co/sYgR4V5WaN','https://t.co/1BN3dJ7WfU',
    'http://t.co/6eryhurbVY')
    imageCrawler = ImageCrawler()
    i = 0
    for url in urls:
        print 'image url = ', imageCrawler.crawl(url)
        i = i+1
        time.sleep(1)
        if i==1000:
            break
    print imageCrawler.domains

    # r = {u'www.channelnewsasia.com': 9, u'boxgame.tistory.com': 1, u'eternallightbaek.tumblr.com': 1, u'www.nea.gov.sg': 6, u'amp.twimg.com': 2, u'1995-1013.com': 1, u'cfile1.uf.tistory.com': 2, u'farm1.staticflickr.com': 3, u'a12382480fc1a663bb3aeb4d914382b1091fa202-www.googledrive.com': 1, u'cfile24.uf.tistory.com': 2, u'www.newsen.com': 1, u'loveustudio.tistory.com': 1, u'www.allkpop.com': 5, u'i.imgur.com': 6, u'twitter.com': 376, u't.co': 15, u't1.daumcdn.net': 3, u'cafe.daum.net': 1, u'www.melon.com': 1, u'cfile6.uf.tistory.com': 1, u'www.infinite-effect-thailand.com': 2, u'www.wowkorea.jp': 3, u'farm6.staticflickr.com': 1, u'www.youtube.com': 11, u'cfile3.uf.tistory.com': 2, u'now.smtown.com': 1, u'graphics.straitstimes.com': 1, u'smb2stfinitesubs1.blogspot.sg': 3, u'mdpr.jp': 2, u'www.vh1.com': 1, u'imgur.com': 4, u'www.mediafire.com': 1, u'asia.mtvema.com': 1, u'instagram.com': 3, u'www.wattpad.com': 14, u'vine.co': 9, u'i.instagram.com': 1, u'twishort.com': 1, u'bongbong-2.tistory.com': 1, u'img.tvreport.co.kr': 1}
    # r = sorted(r.items(), lambda x, y: cmp(x[1], y[1]))
    # for url in r:
    #     print url

