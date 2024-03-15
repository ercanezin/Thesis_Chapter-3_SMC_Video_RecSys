from .models import *
import numpy as np


class DecisionSystem(object):
    # [IS_WATCHED, IS_LIKED, IS_DISLIKED]
    """IS_WATCHED = 0
        IS_LIKED = 1
        IS_DISLIKED = -1
    """

    def getdecision(self, bundle, interactionArray):

        pois = list(bundle.poi_set.all().order_by('id'))
        subscribers = list(Subscription.objects.filter(bundle=bundle))
        user_poi_matrix = np.empty((len(subscribers), len(pois),))
        #Replace all empty values with 0.5
        user_poi_matrix[:] = 0.5

        matrix_reference = {}
        reverse_matrix_reference = {}
        for i, poi in enumerate(pois):
            matrix_reference[poi.id] = i
            reverse_matrix_reference[i] = poi

        #Create user
        for i, sub in enumerate(subscribers):
            user_watch_history = list(WatchHistory.objects.filter(user=sub.user))
            for wh in user_watch_history:
                poi_id = wh.video.poi.id

                if poi_id not in matrix_reference:
                    continue

                poi_ref = matrix_reference[poi_id]

                if wh.is_liked == interactionArray[0]:
                    user_poi_matrix[i][poi_ref] = np.sqrt(user_poi_matrix[i][poi_ref])
                if wh.is_liked == interactionArray[1]:
                    user_poi_matrix[i][poi_ref] = np.square(user_poi_matrix[i][poi_ref])
                if wh.is_liked == interactionArray[2]:
                    user_poi_matrix[i][poi_ref] = (user_poi_matrix[i][poi_ref] + np.sqrt(
                        user_poi_matrix[i][poi_ref])) / 2.0

        user_poi_matrix = np.transpose(user_poi_matrix)

        decided_pois = self.decide_n_items(user_poi_matrix, bundle.number_of_final_dest)
        pois = map(lambda k: reverse_matrix_reference[k], decided_pois)

        return {"bundle": bundle, "pois": pois}

    def decide_n_items(self, user_item_matrix, n_places):
        averages = {}
        for i, row in enumerate(user_item_matrix):
            average = self.calculate_average(row)
            averages[i] = average

        ordered_averages = sorted(averages, key=lambda m: averages[m])
        ordered_averages.reverse()

        return ordered_averages[:n_places]

    def calculate_average(self,row):
        if len(row) == 0:
            return 0

        res = 0.0
        for k in row:
            res += k

        return res / len(row)
