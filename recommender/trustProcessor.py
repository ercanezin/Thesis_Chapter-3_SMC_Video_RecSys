from .models import *
import random
import numpy as np


class TrustProcessor(object):

    def get_replaced_video_list(self, vid_ids, rec_vid_ids, user, trusted_user, bundle, RECOMMENDATION_COUNT):
        # pick a random proportion between 1 to half of the recommendation list
        proportion = random.randint(1, round(RECOMMENDATION_COUNT / 2))

        # pick a sample of videos from generated list
        vids = random.sample(vid_ids, proportion)

        # replace videos from user with videos from another randomly picked user
  
        for i, vd in enumerate(vid_ids):
            if vd in vids:
                vid_ids[i] = rec_vid_ids[i]
                video = Video.objects.get(id=vd)
                reclstitem = RecListItem(user=user,
                                         video=video,
                                         bundle=bundle,
                                         is_trust=True,
                                         trust_list_owner=trusted_user,
                                         proportion=proportion)
                reclstitem.save()

        return Video.objects.filter(pk__in=vid_ids)

    def generate_trust_network(self, bundle):

        subscribers = bundle.subscription_set.all()
        user_ids = list(subscribers.values_list("user", flat=True))
        users = list(User.objects.filter(id__in=user_ids))

        user_user_matrix = np.empty((len(user_ids), len(user_ids),))
        user_user_matrix[:] = 0.5

        matrix_reference = {}

        for i, user_id in enumerate(user_ids):
            matrix_reference[user_id] = i

        rec_list_items = list(RecListItem.objects.filter(bundle=bundle, user__in=users))

        video_impact = 0.5 / Video.objects.filter(bundle=bundle).count()

        for rli in rec_list_items:

            if rli.user.id not in matrix_reference:
                continue

            user_ref = matrix_reference[rli.user_id]
            trusted_user_ref = matrix_reference[rli.trust_list_owner_id]

            if user_ref == trusted_user_ref:
                continue

            if rli.is_liked == 1:
                user_user_matrix[user_ref][trusted_user_ref] = user_user_matrix[user_ref][
                                                                   trusted_user_ref] + video_impact
            elif rli.is_liked == -1:
                user_user_matrix[user_ref][trusted_user_ref] = user_user_matrix[user_ref][
                                                                   trusted_user_ref] - video_impact

        weight_array = (np.sum(user_user_matrix, axis=0) - 0.5) / user_ids - 1
