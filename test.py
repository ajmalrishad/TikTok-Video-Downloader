from tiktokapipy.api import TikTokAPI

def get_video_thumbnail(video_url):
    with TikTokAPI() as api:
        # Fetch video information
        video = api.video(video_url)
        # Access the thumbnail URL from the video object
        thumbnail_url = video.video.cover
        return thumbnail_url

# Example usage
video_url = "https://www.tiktok.com/@nhacthieunhii/video/7309059452752121089?is_from_webapp=1&sender_device=pc"
thumbnail_url = get_video_thumbnail(video_url)
print(thumbnail_url)
