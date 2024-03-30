from random import shuffle

from .ratingsPredictor import RatingsPredictor
from .trustProcessor import *


class GenerateRec(object):

    def __init__(self):
        pass

    def generate_rec_list(self, tbundle, user, RECOMMENDATION_COUNT):

        # Get POIs of the Bundle
        pois = list(tbundle.poi_set.all().order_by('id'))
        shuffle(pois)

        # Getall Videos of the Bundle
        all_videos_list = list(Video.objects.filter(bundle=tbundle))
        shuffle(all_videos_list)

        subscribed_users_list = [subscriber.user for subscriber in
                                 list(Subscription.objects.filter(bundle=tbundle))]
        empty_user_videos_matrix = np.full((len(subscribed_users_list), len(all_videos_list)), np.NaN)

        user_videos_matrix = self.generate_user_videos_matrix(
            empty_user_videos_matrix, subscribed_users_list,
            tbundle.id, all_videos_list)

        current_user_pos = subscribed_users_list.index(user)
        rec_indexes = RatingsPredictor().get_recommendations_for_user(current_user_pos, user_videos_matrix,
                                                                      RECOMMENDATION_COUNT)
        video_ids = []
        # Get recommended videos from the database
        for rec_index in rec_indexes:
            video_ids.append(all_videos_list[rec_index].id)

        return video_ids

    @staticmethod
    def generate_user_videos_matrix(empty_user_videos_matrix, subscribed_users_list, bundle_id, videos_dict):
        subscribers_watch_history_list = list(WatchHistory.objects.filter(bundle_id=bundle_id))

        for watch_history in subscribers_watch_history_list:
            video_pos = videos_dict.index(watch_history.video)
            empty_user_videos_matrix[subscribed_users_list.index(watch_history.user)][
                video_pos] = watch_history.is_liked

        return empty_user_videos_matrix
