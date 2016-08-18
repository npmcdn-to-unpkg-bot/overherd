from nytimesarticle import articleAPI
import sys
from time import sleep

# Example usage: "python Samsara virginia 20150827 20150827 0-0"
# where virginia is the keyword, 20150827 is the beginning and end date, and 0-0 indicates pages 0 to 0

"""
PURPOSE
---------------------------------------
Quick way to get old NYTimes articles via keyword(s). Makes it easier to get information on, for example, 
past market declines. See http://www.bloomberg.com/news/articles/2015-08-24/here-s-what-usually-happens-to-markets-after-the-s-p-500-drops-five-percent-in-a-week


SOURCE
---------------------------------------
http://developer.nytimes.com/docs/read/article_search_api_v2


FOLLOWING PARAMETERS CAN BE PASSED IN
---------------------------------------
q:				search query term
fq:				see http://developer.nytimes.com/docs/read/article_search_api_v2#filters
begin_date: 	YYYYMMDD
end_date: 		YYYYMMDD
sort: 			"newest" or "oldest"
page: 			integer, set of ten articles at a time


FOLLOWING PARAMETERS NOT IMPLEMENTED HERE
---------------------------------------
fl: 			list of fields, but just include everything
hl: 			boolean for highlighting 
facet_field: 	see the article search api
callback: 		name of the function API call results will be passed to
"""

# Andrew's key
NYT_API_KEY = "a5a55bf350d53e96601488b6d633a68f:4:61276569"

class Samsara(object):
	def __init__(self, api_key=NYT_API_KEY):
		self.nyt_api = articleAPI(api_key)

	def searchAPI(self, **kwargs):
		return self.nyt_api.search(**kwargs)

	# simply require keyword, dates, and page of records for now
	# pages is a string of form "0-9", denoting pages 0 to 9, or the first 100 results
	def search(self, q, begin_date, end_date, pages="all", sort="newest", fq=None):
		records = []
		
		if (pages != "all"): 
			pageRange = pages.split('-')
		else: 
			pageRange = ["0", "9000"]

		firstPage = int(pageRange[0])
		secondPage = int(pageRange[1])
	
		for page in range(firstPage, secondPage+1):
			sleep(0.1)
			articles = self.searchAPI(q=q, begin_date=begin_date, end_date=end_date, page=page, sort=sort, fq=fq)
			articles = articles['response']['docs']
			if len(articles) == 0: break
			records.extend(articles)

		return records