"""
This module implements a class for shapley values allocation as fair payoff
distribution between players in cooperative game
"""

import numpy as np
from itertools import combinations
from random import sample, seed
from math import factorial, ceil, isnan
from scipy.special import binom
seed(666)


def powerset(iterable):
    r"""
    The powerset is the set of all possible subsets of a set in no particular order.
    Exemple : for the list [1, 2, 3], the power set is [[],[1],[2],[3],[1, 2],[1, 3],[2, 3],[1, 2, 3]]
    """

    seed(666)
    N = len(iterable)
    N_Max = 15

    if N <= N_Max :
        for i in range(len(iterable),-1, -1) :
            for comb in combinations(iterable, i) :
                yield comb

    elif N > N_Max :
        for i in range(len(iterable),-1, -1):
            nb_coalition_size_i = factorial(N)/(factorial(i)* factorial(N-i))
            nb_coalition_to_select = int(ceil(nb_coalition_size_i * 2**N_Max / 2**N))
            
            if nb_coalition_size_i > 500  and nb_coalition_to_select <= 500 :
                nb_coalition_to_select = 500
            elif nb_coalition_size_i <= 500  and nb_coalition_to_select <= 500 :
                nb_coalition_to_select =  nb_coalition_size_i
            
            j = 0
            while j < nb_coalition_to_select:
                comb = tuple(sorted(sample(iterable, i)))
                j += 1
                yield comb


class Payoff():
    r"""
    An object representing a payoff model for a fair distribution of the total payoff between players.
    It primarily used to compute the Shapley value but it also provides methods to check some
    desirable properties of Shapley values : Efficiency, Symmetry, Linearity, Null player.
    The Shapley values are the only allocation vectors that satisfies all those properties.
    """
    
    def __init__(self, characteristic_function):
        r"""
        Initializes a co-operative game and checks the inputs.
        """
        
        if not isinstance(characteristic_function, dict):
            raise TypeError("characteristic function must be a dictionary")

        self.ch_f = characteristic_function
        
        for key in list(self.ch_f):
            if len(str(key)) == 1 and not isinstance(key, tuple):
                self.ch_f[(key,)] = self.ch_f.pop(key)
            elif not isinstance(key, tuple):
                raise TypeError("key must be a tuple")

        for key in list(self.ch_f):
            sortedkey = tuple(sorted(key))
            self.ch_f[sortedkey] = self.ch_f.pop(key)
        
        self.player_list = max(characteristic_function, key=lambda key: len(key))
        self.number_players = len(self.player_list)
        
        for coalition in powerset(self.player_list):
            if tuple(sorted(coalition)) not in self.ch_f:
                raise ValueError("characteristic function must be the power set")
        

    def shapley_value(self):
        r"""
        Return the Shapley value for ``self``.
        The Shapley value is the fair payoff vector and is computed by
        the following formula:
        """
        
        payoff_vector = {}
        N = len(self.player_list)
        N_Max = 15
        
        if N <= N_Max :
            for player in self.player_list:
                weighted_contribution = 0
                for coalition in powerset(self.player_list):
                    if coalition :  # If non-empty
                        k = len(coalition)
                        weight = 1 / (binom(N, k) * k)
                        t = tuple(p for p in coalition if p != player)
                        weighted_contribution += weight * (self.ch_f[tuple(coalition)] - self.ch_f[t])
                        
                if weighted_contribution >= 0 :
                    payoff_vector[player] = weighted_contribution
                else :
                    #payoff_vector[player] = weighted_contribution
                    payoff_vector[player] = 0
        
        elif N > N_Max :
            char_function = self.ch_f

            for player in self.player_list:

                weighted_contribution = 0

                for j in range(1, len(self.player_list)):
                    weight = 1 / (N-j)

                    Mkj = {k: v for k, v in char_function.items() if len(k) == j and player in k}
                    Mj = {k: v for k, v in char_function.items() if len(k) == j}

                    avg_Mkj_tmp = np.array(list(Mkj.values()))
                    avg_Mj_tmp  = np.array(list(Mj.values()))

                    avg_Mkj = avg_Mkj_tmp[~np.isnan(avg_Mkj_tmp)].mean()
                    avg_Mj  = avg_Mj_tmp[~np.isnan(avg_Mj_tmp)].mean()

                    if isnan(avg_Mkj - avg_Mj) == True :
                        diff_avg = 0
                    else :
                        diff_avg = avg_Mkj - avg_Mj
                    
                    weighted_contribution += weight * diff_avg
                    
                dict_grand_coalition = {k: v for k, v in char_function.items() if len(k) == N}
                grand_coalition_utility = np.array(list(dict_grand_coalition.values())).mean()

                weighted_contribution += 1/N * grand_coalition_utility
                
                if weighted_contribution >= 0 :
                    payoff_vector[player] = weighted_contribution
                else :
                    #payoff_vector[player] = weighted_contribution
                    payoff_vector[player] = 0
                    
        return payoff_vector


    def number_of_players(self):
        r"""
        Return a concise description of ``self``
        """
        return "This is a {} players co-operative game".format(self.number_players)
