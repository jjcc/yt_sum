import os
import yt_dlp
import pandas as pd


def get_video_transcript(video_id, output_file):
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


def get_list_from_channel(channel_id):
    channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return [{
            "title": video.get("title"),
            "id": video.get("id"),
            "upload_date": video.get("upload_date"),
            "duration": video.get("duration"),
            "view_count": video.get("view_count"),
            "webpage_url": video.get("webpage_url")
        } for video in info.get("entries", [])]


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




if __name__ == "__main__":
    #####1. get video list from a channel
    #channel_url = "https://www.youtube.com/@dylanrieger7651/videos" 
    #videos = get_channel_video_list(channel_url, limit=190)
    #df = pd.DataFrame(videos)
    #df.to_csv("output/channel_videos.csv", index=False, encoding='utf-8-sig')
    #for v in videos:
    #    print(v)

    ####2. get metadata for a specific video
    #VIDEO_ID = "Jhvyjm7XlZQ"
    #url = f"https://www.youtube.com/watch?v={VIDEO_ID}"
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
    #metadata = get_video_metadata(url)
    #with open("output/video_metadata.json", "w", encoding="utf-8") as f:
    #    import json
    #    json.dump(metadata, f, ensure_ascii=False, indent=4)


    #print(metadata)
    #output_dir = "output"
    #output_file = f"{output_dir}/my_subs.en.vtt"
    #os.makedirs(output_dir, exist_ok=True)
    #get_video_transcript(VIDEO_ID, output_file)
    #print(f"Transcript for video {VIDEO_ID} downloaded to {output_file}")
Get $50 Off Alpha Picks: https://link.seekingalpha.com/3MC6TXH/4HKP84/
