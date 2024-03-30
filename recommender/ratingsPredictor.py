import math
import numpy as np


class RatingsPredictor(object):
    def __init__(self):
        pass

    def get_recommendations_for_user(self, user, user_item_matrix, n_rec):
        pearson_coefficients = self.calculate_pearson_coefficients(user_item_matrix)
        ratings = {}
        for k in range(0, len(user_item_matrix[0])):
            pearson_rating = self.predict_pearson_rating((user, k), user_item_matrix, pearson_coefficients)
            if math.isnan(pearson_rating):
                pearson_rating = 0.0
            ratings[k] = pearson_rating

        ordered_items = sorted(ratings, key=ratings.get)
        ordered_items.reverse()

        recs = []
        for oitem in ordered_items:
            if len(recs) >= n_rec:
                break
            if math.isnan(user_item_matrix[user][oitem]):
                recs.append(oitem)

        return recs

    @staticmethod
    def calculate_means(ur_matrix):
        means = []
        for row in ur_matrix:
            summ = 0
            cnt = 0
            for val in row:
                if math.isnan(val):
                    continue
                summ += val
                cnt += 1
            if cnt == 0:
                means.append(0.0)
                continue
            mean = float(summ) / float(cnt)
            means.append(mean)

        return means

    def calculate_mean_centred_matrix(self, ur_matrix):
        means = self.calculate_means(ur_matrix)
        mean_centred_matrix = []
        for i, row in enumerate(ur_matrix):
            mean_centred_matrix.append([])
            for j in row:
                if math.isnan(j):
                    mean_centred_matrix[i].append(np.NaN)
                    continue
                mean_centred_matrix[i].append(j - means[i])
        return mean_centred_matrix

    def calculate_pearson_coefficients(self, ur_matrix):
        mean_centred_matrix = self.calculate_mean_centred_matrix(ur_matrix)
        pearson_coefficients = np.zeros((len(ur_matrix), len(ur_matrix)))

        for i in range(0, len(ur_matrix)):
            for j in range(i, len(ur_matrix)):
                if i == j:
                    pearson_coefficients[i][j] = 1.0
                    continue
                coeff = self.pearson_coefficient(mean_centred_matrix[i], mean_centred_matrix[j])
                pearson_coefficients[i][j] = pearson_coefficients[j][i] = coeff

        return pearson_coefficients

    @staticmethod
    def pearson_coefficient(su, sv):
        num = 0
        denu = 0
        denv = 0
        for i in range(0, len(su)):
            if math.isnan(su[i]) or math.isnan(sv[i]):
                continue
            num += su[i] * sv[i]
            denu += su[i] ** 2
            denv += sv[i] ** 2

        den = np.sqrt(denu) * np.sqrt(denv)
        if den == 0:
            return 0.0
        return float(num) / den

    @staticmethod
    def predict_pearson_rating(user_rating, ur_matrix, pearson_coefficients):
        k = 1  # kNN - adjust based on number of users?

        user_coefficient_pairs = []
        for i, u in enumerate(ur_matrix):
            if i == user_rating[0]:
                continue
            coefficient = pearson_coefficients[i][user_rating[0]]
            user_coefficient_pairs.append((i, coefficient))
        user_coefficient_pairs.sort(key=lambda x: x[1])
        user_coefficient_pairs.reverse()
        user_coefficient_pairs = user_coefficient_pairs[0:k]

        num = 0.0
        den = 0.0
        for p in user_coefficient_pairs:
            num += ur_matrix[p[0]][user_rating[1]] * p[1]
            den += p[1]

        if den == 0:
            return 0.0
        return num / den
