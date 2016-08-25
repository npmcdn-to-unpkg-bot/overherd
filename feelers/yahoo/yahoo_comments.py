import requests
import json
from bs4 import BeautifulSoup
import re
import pdb

YAHOO_NEWS_URLS = ["https://www.yahoo.com/news/"]
YAHOO_COMMENT_SERVICE_URL = 'https://www.yahoo.com/news/_td/api/resource/CommentsService.comments;count=100;publisher=news-en-US;sortBy=highestRated;uuid=%s?bkt=Headline-Testing-Control&dev_info=0&device=desktop&intl=us&lang=en-US&site=fp&returnMeta=true'

def main():
	uuids = get_uuids(YAHOO_NEWS_URLS[0])
	comments = get_yahoo_comments(uuids)
	pdb.set_trace()

# GET COMMENTS FOR ARTICLES
# take in a dictionary of {uuid => {title, url}}
# return dictionary of {uuid => {"comments": comment_json}}
def get_yahoo_comments(uuids):
	comments = {}
	for uuid in uuids:
		comment_json = get_yahoo_comments_for_article(uuid)
		comments[uuid] = {"article_headline": uuids[uuid]['title'], "comments": comment_json}
		
	return comments

def get_yahoo_comments_for_article(uuid):
	r = requests.get(YAHOO_COMMENT_SERVICE_URL % uuid)
	comment_json = json.loads(r.text)
	return comment_json

# GET ARTICLE INFORMATION
def get_uuids(yahoo_link):
	# stream items have their own article id and have 
	# a list of storyline items which have their own article ids
	def get_stream_items(yahoo_json):
		stream_items = yahoo_json['context']['dispatcher']['stores']['StreamStore']['streams']
		stream_items = stream_items[stream_items.keys()[0]]
		stream_items = stream_items['data']['stream_items']
		return stream_items


	pattern = '({"context":.+});'
	r = requests.get(yahoo_link)
	match = re.findall(pattern, r.text)[0]
	yahoo_json = json.loads(match)
	stream_items = get_stream_items(yahoo_json)

	article_uuids = {}

	for stream_item in stream_items:
		if "id" in stream_item:
			article_uuids[stream_item['id']] = {"title": stream_item['title'], "url": stream_item['url']}

		if "storyline" in stream_item:
			for storyline in stream_item['storyline']:
				if "id" in storyline:
					article_uuids[storyline['id']] = {"title": storyline['title'], "url": storyline['url']}

	return article_uuids


if __name__ == "__main__":
	main()
