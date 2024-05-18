import requests
import  isodate
from urllib.parse import urlparse, parse_qs

def get_video_id_from_url(url):
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]
    return None

def get_youtube_video_duration(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={api_key}"
    response = requests.get(url)
    data = response.json()
    duration = isodate.parse_duration(data['items'][0]['contentDetails']['duration'])
    return duration.total_seconds()

