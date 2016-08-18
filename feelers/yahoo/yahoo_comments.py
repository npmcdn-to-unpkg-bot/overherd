import requests
import json
from bs4 import BeautifulSoup
import re
import pdb

YAHOO_NEWS_URLS = ["https://www.yahoo.com/news/"]
YAHOO_COMMENT_SERVICE_URL = 'https://www.yahoo.com/news/_td/api/resource/CommentsService.comments;count=100;publisher=news-en-US;sortBy=highestRated;uuid=%s?bkt=Headline-Testing-Control&dev_info=0&device=desktop&intl=us&lang=en-US&site=fp&returnMeta=true'

def main():
	uuids = get_uuids(YAHOO_NEWS_URLS[0])
	comments = get_comments(uuids)

# take in a dictionry of {uuid => {title, url}}
def get_comments(uuids):
	comments = {}
	for uuid in uuids:
		r = requests.get(YAHOO_COMMENT_SERVICE_URL % uuid)
		comment_json = json.loads(r.text)
		comments[uuid] = {"comments": comment_json}

	return comments

def get_uuids(yahoo_link):
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

# sometimes there are uuids that aren't part of Yahoo's service??
def is_yahoo_uuid():
	pass	

def get_stream_items(yahoo_json):
	stream_items = yahoo_json['context']['dispatcher']['stores']['StreamStore']['streams']
	stream_items = stream_items[stream_items.keys()[0]]
	stream_items = stream_items['data']['stream_items']
	return stream_items

if __name__ == "__main__":
	main()
