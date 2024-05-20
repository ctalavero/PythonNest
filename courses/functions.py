import requests
import  isodate
from urllib.parse import urlparse, parse_qs
from moviepy.editor import VideoFileClip
from typing import Optional

def get_video_id_from_url(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.

    Parameters:
    url (str): The YouTube URL.

    Returns:
    str: The video ID, or None if the URL does not contain a video ID.
    """
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]
    return None

def get_youtube_video_duration(video_id: str, api_key: str) -> float:
    """
    Retrieves the duration of a YouTube video in seconds.

    Parameters:
    video_id (str): The ID of the YouTube video.
    api_key (str): The API key to use for the YouTube Data API v3.

    Returns:
    float: The duration of the video in seconds.
    """
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={api_key}"
    response = requests.get(url)
    data = response.json()
    duration = isodate.parse_duration(data['items'][0]['contentDetails']['duration'])
    return duration.total_seconds()

def get_video_duration(video_path):
    """
    Retrieves the duration of a video file in seconds.

    Parameters:
    video_path (str): The path to the video file.

    Returns:
    float: The duration of the video in seconds.
    """
    clip = VideoFileClip(video_path)
    duration = clip.duration # in seconds
    return duration