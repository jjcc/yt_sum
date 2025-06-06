import os
from time import sleep
import yt_dlp
import pandas as pd
from service.helper import clean_vtt_to_script
from dotenv import load_dotenv


def get_video_transcript(video_id, output_file):
    """
    Downloads the auto-generated English subtitles for a YouTube video.
    Args:
        video_id (str): The YouTube video ID.
        output_file (str): The file path to save the subtitles.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    os.system(f'yt-dlp --write-auto-sub --sub-lang en --skip-download -o "{output_file}" "{video_url}"')


def get_video_metadata(video_url):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return {
            "title": info.get("title"),
            "upload_date": info.get("upload_date"),  # format: YYYYMMDD
            "duration": info.get("duration"),        # in seconds
            "channel": info.get("uploader"),
            "view_count": info.get("view_count"),
            "description": info.get("description"),
            "tags": info.get("tags"),
            "webpage_url": info.get("webpage_url")
        }


def get_channel_video_list(channel_url, limit=10):
    '''Fetches a list of videos from a YouTube channel.
    Args:'''
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # No need to download videos
        'playlistend': limit   # Limit number of videos
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        videos = info.get('entries', [])
        return [
            {
                'title': v.get('title'),
                'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                'id': v.get('id'),
            }
            for v in videos
        ]




def get_all_transcripts(get_video_transcript, row, index):
    #url = row['webpage_url'].values[0]
    url = row.webpage_url
    VIDEO_ID = url.split('v=')[-1]  # Extract video ID from URL
    #udate = row['upload_date'].values[0]  # Get upload date
    udate = row.upload_date # Get upload date
    print(f"Video ID: {VIDEO_ID}, Upload Date: {udate}")
    output_dir = "output"
    output_file_noext = f"{output_dir}/transcript/{udate}"
    output_file = f"{output_file_noext}.en.vtt"
    os.makedirs(output_dir, exist_ok=True)
    get_video_transcript(VIDEO_ID, output_file_noext)
    sleep(1)  # Wait for the file to be created
    # convert
    with open(output_file, "r", encoding="utf-8") as f:
        vtt_content = f.read()
    cleaned = clean_vtt_to_script(vtt_content, is_file_path=False)
    with open(f"output/cleaned/{udate}.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"{index}:Transcript for video {VIDEO_ID} downloaded to {output_file}")


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
    case = 3  # Set the case number to run the desired part of the scraper
    main(case)   

   
    #####1. get video list from a channel
    #channel_url = "https://www.youtube.com/@dylanrieger7651/videos" 
    #videos = get_channel_video_list(channel_url, limit=190)
    #df = pd.DataFrame(videos)
    #df.to_csv("output/channel_videos.csv", index=False, encoding='utf-8-sig')
    #for v in videos:
    #    print(v)

    ####2. get metadata for a specific video
    #df = pd.read_csv("output/channel_videos.csv", encoding='utf-8-sig')
    #metalist = []
    #for index, row in df.iterrows():
    #    video_id = row['id']
    #    video_url = f"https://www.youtube.com/watch?v={video_id}"
    #    metadata = get_video_metadata(video_url)
    #    metalist.append(metadata)
    #    print(f"Metadata for {video_id}: {metadata}")
    #df_metadata = pd.DataFrame(metalist)
    #df_metadata.to_csv("output/video_metadata.csv", index=False, encoding='utf-8-sig')


    ####3. get transcript for a specific video
    #df = pd.read_csv("output/video_metadata.csv", encoding='utf-8-sig')
    #df0 = df.iloc[0:1]  # Get the first row
    #for index, row in df.iterrows():
    #    get_all_transcripts(get_video_transcript, row, index)
    #    #print(f"Processing video {index + 1}/{len(df0)}: {row['title']}")
