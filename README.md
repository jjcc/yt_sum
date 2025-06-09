# yt_sum
Youtube summary using LLM

## Scripts

There are 3 scripts for now

* scraper.py -- Scrap transcript from Youtube channel
* extracter.py -- Extract the opinions from the transcript. Current version extract stock symbol mentioned in the content along with youtuber's opinion. It can be customized according to requirements 
* evaluator.py -- Evaluate the return on the mentioned stocks with 1 week, 2 weeks, 1 month, and so on. 

## Requirement
* An .env file should be created , with Open AI API key and Youtube channel filled
* The code tested with Python 3.10+

## Steps to use the scripts:

* Use the scraper to retrieve  the transcripts and date from all the video of  a Youtube channel
* Use the extractor to convert the scrapped scripts into useful datasets to be used in the next step
* Use the evaluateor to: download all the stock prices related to the mentioned stocks, calculated the return on later dates