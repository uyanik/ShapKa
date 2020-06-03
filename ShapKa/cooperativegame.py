"""
This module implements a class to build the characteristic function of a cooperative game.
"""

import numpy as np
from itertools import combinations
from random import sample, seed
from math import factorial, ceil
seed(666)

class Game(object):
    r"""
    An object representing a co-operative game.
    A co-cooperative game with n-players is characterised by a characteristic function v(S)
    The characteristic function return for every potential coalition S, the associated utility (or payoff)
    """
    
    def __init__(self, X, y,
                 y_dissat_upperbound, y_sat_lowerbound,
                 X_dissat_upperbound, X_sat_lowerbound,
                 weight):
        self._X = X
        self._y = y
        self._N = X.shape[1]
        self._N_Max = 15
        self._y_dissat_upperbound = y_dissat_upperbound
        self._y_sat_lowerbound = y_sat_lowerbound
        self._X_dissat_upperbound = X_dissat_upperbound
        self._X_sat_lowerbound = X_sat_lowerbound
        self._weight = weight
        self._powerset = None
    
    def PowerSet(self):
        r"""
        The powerset all possible subsets of a set of players in no particular order.
        Exemple : for the list [1, 2, 3], the power set is
        [[],[1],[2],[3],[1, 2],[1, 3],[2, 3],[1, 2, 3]]
        """
        seed(666)
        grand_coalition = [i for i in range(0, self._N)]
        
        set_of_all_coalitions = set([])

        if self._N <= self._N_Max :
            for i in range(len(grand_coalition),-1,-1):
                for element in combinations(grand_coalition, i):
                    set_of_all_coalitions.add(element)

            set_of_all_coalitions = {i : None for i in set_of_all_coalitions}

        elif self._N > self._N_Max :
            set_of_all_coalitions_tmp = set([])
        
            for i in range(len(grand_coalition),-1,-1):
                nb_coalition_size_i = factorial(self._N) / (factorial(i) * factorial(self._N-i))
                nb_coalition_to_select = int(ceil(nb_coalition_size_i * 2**self._N_Max / 2**self._N))
                
                    
                if nb_coalition_size_i > 500  and nb_coalition_to_select <= 500 :
                    nb_coalition_to_select = 500
                elif nb_coalition_size_i <= 500  and nb_coalition_to_select <= 500 :
                    nb_coalition_to_select =  nb_coalition_size_i
                
                j = 0
                while j < nb_coalition_to_select:
                    element = tuple(sorted(sample(grand_coalition, i)))
                    set_of_all_coalitions.add(element)
                    j += 1
            
            for player in grand_coalition:
                element = tuple(p for p in grand_coalition if p == player)
                if element not in set_of_all_coalitions :
                    set_of_all_coalitions.add(element)
                        
            set_of_all_coalitions = set_of_all_coalitions.union(set_of_all_coalitions_tmp)

        self._powerset = set_of_all_coalitions

        print('Number of sampled coalitions:',  len(set_of_all_coalitions), ' / ', 2**self._N)

        return set_of_all_coalitions


    def UtilityFunction(self, coalition, analysis):
        r"""
        We compute the utility for each coalition. Utility function is defined as
        the difference between the Reach level and Noise level.
        The Reach level shows the prevalence of failure on any attributes
        in the coalition among those who are dissatisfied overall.
        The Noise level shows the prevalence of failure on any attributes
        in the coalition among those who are satisfied overall
        """

        if analysis == 'kda':
            idx_y_dissat = np.where(self._y <= self._y_dissat_upperbound)
            idx_y_notdissat = np.where(self._y > self._y_dissat_upperbound)
            idx_X_dissat_and_y_dissat = np.where(np.any(self._X[idx_y_dissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
            idx_X_dissat_and_y_notdissat = np.where(np.any(self._X[idx_y_notdissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
            y_dissat = np.nansum(self._weight[idx_y_dissat[0]])
            y_notdissat = np.nansum(self._weight[idx_y_notdissat[0]])
            X_dissat_and_y_dissat = np.nansum(self._weight[idx_X_dissat_and_y_dissat[0]])
            X_dissat_and_y_notdissat = np.nansum(self._weight[idx_X_dissat_and_y_notdissat[0]])
            reach = X_dissat_and_y_dissat / y_dissat
            noise = X_dissat_and_y_notdissat / y_notdissat 
            
        elif analysis == 'kea':
            idx_y_sat = np.where(self._y >= self._y_sat_lowerbound)
            idx_y_notsat = np.where(self._y < self._y_sat_lowerbound)
            idx_X_sat_and_y_sat = np.where(np.any(self._X[idx_y_sat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
            idx_X_sat_and_y_notsat = np.where(np.any(self._X[idx_y_notsat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
            y_sat = np.nansum(self._weight[idx_y_sat[0]])
            y_notsat = np.nansum(self._weight[idx_y_notsat[0]])
            X_sat_and_y_sat = np.nansum(self._weight[idx_X_sat_and_y_sat[0]])
            X_sat_and_y_notsat = np.nansum(self._weight[idx_X_sat_and_y_notsat[0]])
            reach = X_sat_and_y_sat / y_sat
            noise = X_sat_and_y_notsat / y_notsat
            
        #utility = np.nansum(coalition)
        utility = (reach - noise) * 100

        return utility


    def CharacteristicFunction(self, analysis):
        r"""
        The characteristic function v describes the worth of each coalition.
        The goal is to split the worth (defined by the characteristic function)
        among the players in a fair way
        """
        return {tuple(coalition) : self.UtilityFunction(coalition, analysis)
                for coalition in self.PowerSet()}