# -*- coding: utf-8 -*-
"""
     video_id (str): The YouTube video ID.
     output_file (str): The file path to save the subtitles.
"""
import os
import pandas as pd
from dotenv import load_dotenv
from service.helper import get_all_transcripts, get_video_transcript
from service.helper import get_channel_video_list, get_video_metadata



def main(case=0):
    """
    Main function to run the scraper.
    Args:
        case (int): The case number to determine which part of the scraper to run.
                     0 - Run all parts
                     1 - Get video list from channel
                     2 - Get metadata for specific videos
                     3 - Get transcripts for specific videos
    """
    load_dotenv()
    channel_url = os.getenv("YOUTUBE_CHANNEL_URL")
    if case in (0, 1):
        videos = get_channel_video_list(channel_url, limit=190)
        df = pd.DataFrame(videos)
        df.to_csv("output/channel_videos.csv", index=False, encoding='utf-8-sig')
        print(f"Video list saved to output/channel_videos.csv with {len(videos)} videos.")
    if case in (0,2):
        df = pd.read_csv("output/channel_videos.csv", encoding='utf-8-sig')
        metalist = []
        for index, row in df.iterrows():
            video_id = row['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            metadata = get_video_metadata(video_url)
            metalist.append(metadata)
            print(f"Metadata for {video_id}: {metadata}")
        df_metadata = pd.DataFrame(metalist)
        df_metadata.to_csv("output/video_metadata.csv", index=False, encoding='utf-8-sig')
    if case in (0, 3):
        df = pd.read_csv("output/video_metadata.csv", encoding='utf-8-sig')
        for index, row in df.iterrows():
            get_all_transcripts(get_video_transcript, row, index)
            print(f"Processing video {index + 1}/{len(df)}: {row['title']}")



if __name__ == "__main__":
    #case = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    mycase = 2  # Set the case number to run the desired part of the scraper
    main(mycase)  
