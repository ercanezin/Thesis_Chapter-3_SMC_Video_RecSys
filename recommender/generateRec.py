from .models import *
from random import shuffle
import numpy as np
from .ratingsPredictor import RatingsPredictor
from .trustProcessor import *


class GenerateRec(object):
    def generate_rec_list(self, tbundle, user, RECOMMENDATION_COUNT):

        # Get POIs of the Bundle
        pois = list(tbundle.poi_set.all().order_by('id'))
        shuffle(pois)
        pois_dict = {}
        videos_dict = {}
        reverse_videos_dict = {}

        all_videos = []
        wh_count = 0

        # PICK RANDOM VIDEOS FOR EACH POI
        # Get 9 videos from each video pool of the POIs
        for poi in pois:

            vids = list(poi.video_set.all().order_by('id'))
            shuffle(vids)

            for vid in vids:
                videos_dict[vid.id] = len(videos_dict)
                reverse_videos_dict[len(reverse_videos_dict)] = vid.id

            pois_dict[poi.location_name] = vids[:RECOMMENDATION_COUNT]  # Take first 9 videos from the list
            all_videos += vids

            user_wh = list(WatchHistory.objects.filter(user=user, bundle_id=tbundle.id))

            wh_count = len(user_wh)

        # if user have watched at least 10 percent of the videos belonging to a subscription show recommended videos
        if wh_count != 0 and len(all_videos) / wh_count < 10:

            # USER x VIDEO MATRIX CREATION
            # Make an empty matrix with user rows and video columns
            subs = list(Subscription.objects.filter(bundle=tbundle))
            user_item_matrix = np.empty((len(subs), len(all_videos),))
            user_item_matrix[:] = np.NaN

            # Set values in the matrix to the correct user/item row/column
            user_pos = 0
            number_of_users_watched_videos = 0

            for i, sub in enumerate(subs):

                if sub.user.id == user.id:
                    user_pos = i

                watch_histories = list(WatchHistory.objects.filter(user=sub.user))
                wh_count = 0

                for wh in watch_histories:
                    if wh.video.id in videos_dict:
                        wh_count += 1
                        item_pos = videos_dict[wh.video.id]
                        user_item_matrix[i][item_pos] = wh.is_liked

                # to count how many users watched at least 10% of videos based on subscription
                if wh_count != 0 and len(all_videos) / wh_count < 10:
                    number_of_users_watched_videos += 1

            # to check if half of users have watched videos
            if len(subs) - 2 * number_of_users_watched_videos <= 0:
                # Generate top recommendation_count recommendations for the user
                res = RatingsPredictor().get_recommendations_for_user(user_pos, user_item_matrix, RECOMMENDATION_COUNT)
                video_ids = []

                # Get recommended videos from the database
                for r in res:
                    video_ids.append(reverse_videos_dict[r])

            return video_ids
