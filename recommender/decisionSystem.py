from .models import *
import numpy as np
from .trustProcessor import TrustProcessor
from .interaction_types import InteractionType


class DecisionSystem(object):

    def __init__(self):
        pass

    @staticmethod
    def getdecision(bundle):

        pois = list(bundle.poi_set.all().order_by('id'))
        subscribers = [subsciption.user for subsciption in
                       list(Subscription.objects.filter(bundle=bundle).order_by('user_id'))]

        # Create user_poi_matrix and trust_user_poi_matrix
        user_poi_matrix = np.zeros((len(subscribers), len(pois)), dtype=float)

        user_poi_matrix[user_poi_matrix == 0] = 0.5

        # Create user poi matrix
        watch_histories = WatchHistory.objects.filter(bundle=bundle)
        for wh in watch_histories:
            poi_index = pois.index(wh.video.poi)
            user_index = subscribers.index(wh.user)

            if wh.is_liked == InteractionType.LIKED.value:  # like
                user_poi_matrix[user_index, poi_index] = np.sqrt(user_poi_matrix[user_index, poi_index])
            elif wh.is_liked == InteractionType.DISLIKED.value:  # dislike
                user_poi_matrix[user_index, poi_index] = np.square(user_poi_matrix[user_index, poi_index])
            elif wh.is_liked == InteractionType.WATCHED.value:  # just watched
                user_poi_matrix[user_index, poi_index] = (user_poi_matrix[user_index, poi_index] + np.sqrt(
                    user_poi_matrix[user_index, poi_index])) / 2.0

        # Calculate averages efficiently
        poi_column_averages = np.mean(user_poi_matrix, axis=0)

        # calculate trust averages
        user_id_weight_dict = TrustProcessor.generate_trust_weights(bundle, subscribers)

        user_weight_list = [user_id_weight_dict[sub.id] for sub in subscribers]
        weighted_user_poi_matrix = user_poi_matrix * np.array(user_weight_list)[:, np.newaxis]
        weighted_user_poi_averages = np.mean(weighted_user_poi_matrix, axis=0)

        ordered_indices = np.argsort(poi_column_averages)[::-1]
        ordered_pois_list = [pois[i] for i in ordered_indices]
        ordered_pois_list_values = poi_column_averages[ordered_indices]

        trust_ordered_indices = np.argsort(weighted_user_poi_averages)[::-1]
        trust_ordered_pois_list = [pois[i] for i in trust_ordered_indices]
        trust_ordered_pois_list_values = weighted_user_poi_averages[ordered_indices]

        result_dict = dict()
        result_dict["bundle"] = bundle
        result_dict["pois"] = [poi.location_name.split(', ')[0] for poi in pois]
        result_dict["ordered_pois_list"] = [poi.location_name.split(', ')[0] for poi in ordered_pois_list]
        result_dict["ordered_pois_decision"] = [poi.location_name.split(', ')[0] for poi in ordered_pois_list][
                                               :bundle.number_of_final_dest]
        result_dict["ordered_pois_list_values"] = ordered_pois_list_values
        result_dict["trust_ordered_pois_list"] = [poi.location_name.split(', ')[0] for poi in trust_ordered_pois_list]
        result_dict["trust_ordered_pois_decision"] = \
            [poi.location_name.split(', ')[0] for poi in trust_ordered_pois_list][:bundle.number_of_final_dest]
        result_dict["trust_ordered_pois_list_values"] = trust_ordered_pois_list_values
        result_dict["num_of_final_destionation"] = bundle.number_of_final_dest
        return result_dict
