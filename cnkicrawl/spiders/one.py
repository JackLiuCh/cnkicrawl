import scrapy
import configparser


class CnkiSpider(scrapy.Spider):
    name = "cnki"

    def start_requests(self):
        cp = configparser.ConfigParser()
        cp.read('config.txt', encoding='utf-8')
        keyword = cp.get('Info', 'keyword')
        self.pages = int(cp.get('Crawl', 'pages'))
        self.currPage = 1

        body = {"action": "",
                "ua": "1.11",
                "isinEn": "1",
                "PageName": "ASP.brief_default_result_aspx",
                "DbPrefix": "SCDB",
                "DbCatalog": "中国学术文献网络出版总库",
                "ConfigFile": "SCDBINDEX.xml",
                "db_opt": "CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD",
                "txt_1_sel": "SU$%=|",
                "txt_1_value1": keyword,
                "txt_1_special1": "%",
                "his": "0",
                "parentdb": "SCDB",
                }

        return [scrapy.FormRequest(url='https://kns.cnki.net/kns/request/SearchHandler.ashx', formdata=body, callback=self.parse)]

    def parse(self, response):
        return [scrapy.Request(url='https://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCDB', callback=self.parse2)]

    def parse2(self, response):
        trs = response.selector.css('table.GridTableContent tr[bgcolor]')
        for tr in trs:
            tds = tr.css('td')
            num = tds[0].css('::text').get()
            title = ''.join(tds[1].css('a ::text').getall())
            author = ''.join(tds[2].css('::text').getall()).strip()
            origin = tds[3].css('a::text').get()
            pub_time = tds[4].css('::text').get().strip()
            database = tds[5].css('::text').get().strip()
            yield {'序号':num, '题目':title, '作者':author, '来源':origin, '发表时间':pub_time, '数据库':database}
        
        self.currPage += 1
        if self.currPage <= self.pages:
            yield scrapy.Request(url='https://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCDB&turnpage=1&RecordsPerpage=20&QueryID=0&tpagemode=L&curpage=' + str(self.currPage), callback=self.parse2)