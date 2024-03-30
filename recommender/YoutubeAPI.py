from googleapiclient.discovery import build
from TravelMadeEasy.settings import YOUTUBE_DEVELOPER_KEY


class YoutubeAPI(object):

    def __init__(self, user):
        self.user = user

    def youtube_search(query, max_results):
        YOUTUBE_API_SERVICE_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type="video",
            videoCategoryId='19'
        ).execute()

        videos = []
        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append('%s' % search_result['id']['videoId'])
        return videos
