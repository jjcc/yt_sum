# yt_sum
Youtube summary using LLM

## Scripts

There are 2 scripts for now

* scraper.py -- Scrap transcript from Youtube channel
* extracter.py -- Extract the opinions from the transcript. Current version extract stock symbol mentioned in the content along with youtuber's opinion. It can be customized according to requirements 

## Requirement
* An .env file should be created , with Open AI API key and Youtube channel filled
* The code tested with Python 3.10+