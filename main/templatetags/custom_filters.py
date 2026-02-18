from django import template
from urllib.parse import urlparse, parse_qs
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    Convert various YouTube URL formats to embed URL
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    if not url:
        return ''
    
    # Already an embed URL
    if 'youtube.com/embed/' in url:
        return url
    
    # Extract video ID from different URL formats
    video_id = None
    
    # Format: https://www.youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch' in url:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        video_id = query_params.get('v', [None])[0]
    
    # Format: https://youtu.be/VIDEO_ID
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    
    # Format: https://www.youtube.com/embed/VIDEO_ID
    elif 'youtube.com/embed/' in url:
        video_id = url.split('youtube.com/embed/')[-1].split('?')[0]
    
    if video_id:
        return f'https://www.youtube.com/embed/{video_id}?rel=0'
    
    return url
