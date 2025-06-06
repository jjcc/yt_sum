# create a unit test
import re
import unittest
from pathlib import Path
from dotenv import load_dotenv
import os
from service.helper import clean_vtt_to_script
import pandas as pd




class TestConvert(unittest.TestCase):
    def setUp(self):
        load_dotenv()

    def test_convert(self):
        with open("output/my_subs.en.vtt", "r", encoding="utf-8") as f:
            vtt_content = f.read()
        # sed '/^[0-9]*:[0-9]*:[0-9]*,[0-9]* --> [0-9]*:[0-9]*:[0-9]*,[0-9]*$/d
        #cleaned1 = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*$', '', vtt_content, flags=re.MULTILINE)
        cleaned2 = clean_vtt_to_script("output/my_subs.en.vtt")

        print(cleaned2[:1000])  # Preview first 1000 chars
        pass
    
    def test_shorten(self):
        df = pd.read_csv("output/video_metadata.csv", encoding='utf-8-sig')
        df['description'] = df['description'].apply(lambda x: x[71:160] if isinstance(x, str) else "")
        df.drop(columns=['tags'], inplace=True, errors='ignore')
        df.to_csv("output/video_metadata_short.csv", index=False, encoding='utf-8-sig')
