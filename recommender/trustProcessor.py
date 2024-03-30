from .models import *
import random
import numpy as np
from .interaction_types import InteractionType
import math


class TrustProcessor(object):
    @staticmethod
    def get_replaced_video_list(video_ids, trust_vid_ids, user, trusted_user, bundle, RECOMMENDATION_COUNT):
        # pick a random proportion between 1 to half of the recommendation list
        proportion = random.randint(1, math.ceil(RECOMMENDATION_COUNT / 2))

        # pick indices of a sample of videos from generated list
        rand_vids_ids = random.sample(video_ids, proportion)

        for rep_video_id in rand_vids_ids:
            rep_index = video_ids.index(rep_video_id)
            if trust_vid_ids[rep_index] not in video_ids:
                video_ids[rep_index] = trust_vid_ids[rep_index]
                video = Video.objects.get(id=video_ids[rep_index])
                reclstitem = RecListItem(user=user,
                                         video=video,
                                         bundle=bundle,
                                         is_trust=True,
                                         trust_list_owner=trusted_user,
                                         proportion=proportion)
                reclstitem.save()

        return Video.objects.filter(pk__in=video_ids)

    @staticmethod
    def generate_trust_weights(bundle, subscribers):
        user_ids = [user.id for user in subscribers]

        user_user_matrix = np.zeros((len(user_ids), len(user_ids)), dtype=float)

        recListItems = RecListItem.objects.filter(bundle=bundle, user_id__in=user_ids, is_trust=True)

        # Update user-user matrix with values
        for rli in recListItems:
            watch_histories = WatchHistory.objects.filter(bundle=bundle, user=rli.user, created_on__gte=rli.created_on,
                                                          video=rli.video)
            for wh in watch_histories:
                user_loc = user_ids.index(rli.user_id)
                trusted_user_loc = user_ids.index(rli.trust_list_owner_id)

                if wh.is_liked == InteractionType.LIKED.value:  # like
                    user_user_matrix[user_loc, trusted_user_loc] += (math.sqrt(0.5) - 0.5)
                elif wh.is_liked == InteractionType.WATCHED.value:  # just watched
                    user_user_matrix[user_loc, trusted_user_loc] += (math.sqrt(0.5) - 0.5) / 2

        # Calculate non-reciprocal weights
        non_reciprocal_weights = np.sum(user_user_matrix, axis=0)

        # Normalize between 0 and 1 (min-max normalization)
        normalized_weights = (non_reciprocal_weights - non_reciprocal_weights.min()) / (
                non_reciprocal_weights.max() - non_reciprocal_weights.min())

        # Create the dictionary
        weight_dict = dict(zip(user_ids, normalized_weights))

        return weight_dict
