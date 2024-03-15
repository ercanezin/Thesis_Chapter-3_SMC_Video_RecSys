from googleapiclient.discovery import build


class YoutubeAPI(object):

    def __init__(self, user):
        self.user = user

    def youtube_search(query, max_results):
        DEVELOPER_KEY = 'enter_your_dev_key'
        YOUTUBE_API_SERVICE_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type="videos"
        ).execute()

        videos = []
        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append('%s' % search_result['id']['videoId'])
        return videos
