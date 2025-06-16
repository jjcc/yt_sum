# -*- coding: utf-8 -*-
"""
This module provides helper functions to process YouTube video transcripts.
It includes functions to clean VTT files, download video transcripts, and fetch video metadata.
"""
import os
import re
from pathlib import Path
from time import sleep
import yt_dlp
from twilio.rest import Client


def clean_vtt_to_script(vtt_file_path_or_content, is_file_path=True):
    """
    Converts a VTT (WebVTT subtitle) file to a cleaned script text.
    Reads the specified VTT file, removes timestamps, numbering, empty lines, 
    and duplicate lines caused by overlapping captions. Combines the 
    remaining lines into a single string, removes extra spaces before punctuation, and strips out any HTML tags.

    Args:
        vtt_file_path_or_content (str or Path): The path to the VTT file or the content to be processed.
    Returns:
        str: The cleaned script text extracted from the VTT file.
    """
    if is_file_path:
        lines = Path(vtt_file_path_or_content).read_text(encoding='utf-8').splitlines()
    else:
        lines = vtt_file_path_or_content.splitlines()
    cleaned_lines = []
    previous_line = ""

    for line in lines:
        line = line.strip()

        # Skip empty lines, timestamps, and numbering
        if not line or '-->' in line or re.match(r'^\d+$', line):
            continue

        # Avoid duplications due to overlapping captions
        if line == previous_line:
            continue

        # Append if not redundant
        cleaned_lines.append(line)
        previous_line = line

    # Combine lines and fix common subtitle formatting
    text = " ".join(cleaned_lines)

    # Optional cleanup: Remove extra spaces before punctuation
    text = re.sub(r'\s+([.,?!])', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)

    return text


def get_video_transcript(video_id, output_file):
    """
    Downloads the auto-generated English subtitles for a YouTube video.
    Args:
        video_id (str): The YouTube video ID.
        output_file (str): The file path to save the subtitles.
    Notes:
        - This function is passed to `get_all_transcripts` to download subtitles for each video.
        - The subtitles are saved in VTT format.
        - The function uses yt-dlp to download the subtitles, ensure yt-dlp is installed and configured correctly.
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
                'view_count': v.get('view_count'),
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

    output_file, clear_text_file = extracxt_n_clean_transcript(VIDEO_ID, udate)
    print(f"{index}:Transcript for video {VIDEO_ID} downloaded to {output_file}")

def extracxt_n_clean_transcript(VIDEO_ID, udate):
    """
    Extracts and cleans the transcript for a given YouTube video ID.
    Args:
        
        VIDEO_ID (str): The YouTube video ID.
        udate (str): The upload date of the video in YYYYMMDD format.
        Returns:
        output_file(str): The path to the cleaned transcript file.
    """
    output_dir = "output"
    output_file_noext = f"{output_dir}/transcript/{udate}_{VIDEO_ID}"
    output_file = f"{output_file_noext}.en.vtt"
    os.makedirs(output_dir, exist_ok=True)
    get_video_transcript(VIDEO_ID, output_file_noext)
    sleep(1)  # Wait for the file to be created
    # convert
    with open(output_file, "r", encoding="utf-8") as f:
        vtt_content = f.read()
    cleaned = clean_vtt_to_script(vtt_content, is_file_path=False)
    clear_text_file = f"output/cleaned/{udate}_{VIDEO_ID}.txt"
    with open(clear_text_file, "w", encoding="utf-8") as f:
        f.write(cleaned)
    return output_file, clear_text_file


def get_a_transcript(video_id):
    """
    Downloads the auto-generated English subtitles for a YouTube video.
    Args:
        video_id (str): The YouTube video ID.
        output_file (str): The file path to save the subtitles.
    Notes:
        - This function is passed to `get_all_transcripts` to download subtitles for each video.
        - The subtitles are saved in VTT format.
        - The function uses yt-dlp to download the subtitles, ensure yt-dlp is installed and configured correctly.
    """

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    metadata = get_video_metadata(video_url)  # Fetch metadata to get upload date
    udate = metadata['upload_date']  # Get upload date

    output_file, clear_text_file = extracxt_n_clean_transcript(video_id, udate)
    print(f"Transcript for video {video_id} downloaded to {output_file}")
    return output_file, clear_text_file


def send_sms(message_body="Here's a message from Twilio!", target_numbers=[]):
    """
    Send an SMS message using Twilio.
    Args:
        message_body (str): The body of the SMS message to send.
    """
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    twilio_number = os.environ["TWILIO_PHONE_NUMBER"]
    client = Client(account_sid, auth_token)


    results = []
    for number in target_numbers:
        result = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=number
        )
        results.append(result)
    return results