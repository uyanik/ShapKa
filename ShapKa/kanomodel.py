# -*- coding: utf-8 -*-
"""
This module compute the kano model with shapley values allocation
"""

import numpy as np
import pandas as pd
from ShapKa.cooperativegame import Game
from ShapKa.payoff import Payoff
np.warnings.filterwarnings('ignore')

class KanoModel(object):
    """
    Description
    """
    def __init__(self, df,
                 y_varname, X_varnames,
                 analysis,
                 y_dissat_upperbound, y_sat_lowerbound,
                 X_dissat_upperbound, X_sat_lowerbound,
                 weight_varname = None):
        self._df = df
        self._y_varname  = y_varname
        self._X_varnames = X_varnames
        self._weight_varname = weight_varname
        self._y = self._df[self._y_varname].values
        self._X = self._df[self._X_varnames].values
        self._weight = self._df[self._weight_varname].values if weight_varname is not None else np.ones(self._X.shape[0]).reshape(self._X.shape[0], 1)
        self._analysis  = analysis
        self._N = self._X.shape[1]
        self._y_dissat_upperbound = y_dissat_upperbound
        self._y_sat_lowerbound = y_sat_lowerbound
        self._X_dissat_upperbound = X_dissat_upperbound
        self._X_sat_lowerbound = X_sat_lowerbound
       
    
    def shapley_values(self):

        print("Computing Shapley values: it could take some time ...")

        game = Game(self._X, self._y,
                    self._y_dissat_upperbound, self._y_sat_lowerbound,
                    self._X_dissat_upperbound, self._X_sat_lowerbound,
                    self._weight)

        characteristic_function = game.CharacteristicFunction(self._analysis)

        payoff = Payoff(characteristic_function)

        shapley_values = payoff.shapley_value()

        return shapley_values

    
    def performance_player(self, idx_player):

        if self._analysis == 'kda':
            idx_X_dissat = np.where(self._X[:, [idx_player]] <= self._X_dissat_upperbound)
            X_dissat = sum(self._weight[idx_X_dissat[0]])
            performance_player = X_dissat / sum(self._weight) * 100

        elif self._analysis == 'kea':
            idx_X_sat = np.where(self._X[:, [idx_player]] >= self._X_sat_lowerbound)
            X_sat = np.nansum(self._weight[idx_X_sat[0]])
            performance_player = X_sat / np.nansum(self._weight) * 100

        return performance_player
    
        
    def performance_player(self, ranking_players):

        total_base = np.nansum(self._weight)
        
        if self._analysis == 'kda':
            performance_coalition = []
            for (index_label, row_series) in ranking_players.iterrows():
                coalition = []
                coalition.append(index_label)
                idx_X_dissat = np.where(np.any(self._X[:, coalition] <= self._X_dissat_upperbound, axis=1))
                X_dissat = np.nansum(self._weight[idx_X_dissat[0]])
                performance = X_dissat / total_base * 100
                performance_coalition.append(float(performance))

        elif self._analysis == 'kea':
            performance_coalition = []
            for (index_label, row_series) in ranking_players.iterrows():
                coalition = []
                coalition.append(index_label)
                idx_X_sat = np.where(np.any(self._X[:, coalition] >= self._X_sat_lowerbound, axis=1))
                X_sat = np.nansum(self._weight[idx_X_sat[0]])
                performance = X_sat / total_base * 100
                performance_coalition.append(float(performance))

        return performance_coalition
    
    
    def reach_player(self, ranking_players):

        reach_players = []
        
        if self._analysis == 'kda':
            idx_y_dissat = np.where(self._y <= self._y_dissat_upperbound)
            y_dissat = np.nansum(self._weight[idx_y_dissat[0]])
            for (idx_player, row_series) in ranking_players.iterrows():
                idx_X_dissat_and_y_dissat = np.where(np.any(self._X[idx_y_dissat[0]][:, [idx_player]] <= self._X_dissat_upperbound, axis=1))
                X_dissat_and_y_dissat = np.nansum(self._weight[idx_X_dissat_and_y_dissat[0]])
                reach_player = X_dissat_and_y_dissat / y_dissat * 100
                reach_players.append(float(reach_player))

        elif self._analysis == 'kea':
            idx_y_sat = np.where(self._y >= self._y_sat_lowerbound)
            y_sat = np.nansum(self._weight[idx_y_sat[0]])
            for (idx_player, row_series) in ranking_players.iterrows():
                idx_X_sat_and_y_sat = np.where(np.any(self._X[idx_y_sat[0]][:, [idx_player]] >= self._X_sat_lowerbound, axis=1))
                X_sat_and_y_sat = np.nansum(self._weight[idx_X_sat_and_y_sat[0]])
                reach_player = X_sat_and_y_sat / y_sat * 100
                reach_players.append(float(reach_player))

        return reach_players
    
    
    def noise_player(self, ranking_players):
        
        noise_players = []
        
        if self._analysis == 'kda':
            idx_y_notdissat = np.where(self._y > self._y_dissat_upperbound)
            y_notdissat = np.nansum(self._weight[idx_y_notdissat[0]])
            for (idx_player, row_series) in ranking_players.iterrows():
                idx_X_dissat_and_y_notdissat = np.where(np.any(self._X[idx_y_notdissat[0]][:, [idx_player]] <= self._X_dissat_upperbound, axis=1))
                X_dissat_and_y_notdissat = np.nansum(self._weight[idx_X_dissat_and_y_notdissat[0]])
                noise_player = X_dissat_and_y_notdissat / y_notdissat * 100
                noise_players.append(float(noise_player))

        elif self._analysis == 'kea':
            idx_y_notsat = np.where(self._y < self._y_sat_lowerbound)
            y_notsat = np.nansum(self._weight[idx_y_notsat[0]])
            for (idx_player, row_series) in ranking_players.iterrows():
                idx_X_sat_and_y_notsat = np.where(np.any(self._X[idx_y_notsat[0]][:, [idx_player]] >= self._X_sat_lowerbound, axis=1))
                X_sat_and_y_notsat = np.nansum(self._weight[idx_X_sat_and_y_notsat[0]])
                noise_player = X_sat_and_y_notsat / y_notsat * 100
                noise_players.append(float(noise_player))

        return noise_players


    def reach_coalition(self, ranking_players):

        if self._analysis == 'kda':
            coalition = []
            reach_coalition = []
            idx_y_dissat = np.where(self._y <= self._y_dissat_upperbound)
            y_dissat = np.nansum(self._weight[idx_y_dissat[0]])
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                idx_X_dissat_and_y_dissat = np.where(np.any(self._X[idx_y_dissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
                X_dissat_and_y_dissat = np.nansum(self._weight[idx_X_dissat_and_y_dissat[0]])
                reach = X_dissat_and_y_dissat / y_dissat * 100
                reach_coalition.append(float(reach))

        elif self._analysis == 'kea':
            coalition = []
            reach_coalition = []
            idx_y_sat = np.where(self._y >= self._y_sat_lowerbound)
            y_sat = np.nansum(self._weight[idx_y_sat[0]])
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                idx_X_sat_and_y_sat = np.where(np.any(self._X[idx_y_sat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
                X_sat_and_y_sat = np.nansum(self._weight[idx_X_sat_and_y_sat[0]])
                reach = X_sat_and_y_sat / y_sat * 100
                reach_coalition.append(float(reach))

        return reach_coalition


    def noise_coalition(self, ranking_players):
        coalition = []
        noise_coalition = []
        if self._analysis == 'kda':
            idx_y_notdissat = np.where(self._y > self._y_dissat_upperbound)
            y_notdissat = np.nansum(self._weight[idx_y_notdissat[0]])
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                idx_X_dissat_and_y_notdissat = np.where(np.any(self._X[idx_y_notdissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
                X_dissat_and_y_notdissat = np.nansum(self._weight[idx_X_dissat_and_y_notdissat[0]])
                noise = X_dissat_and_y_notdissat / y_notdissat * 100
                noise_coalition.append(float(noise))

        elif self._analysis == 'kea':
            idx_y_notsat = np.where(self._y < self._y_sat_lowerbound)
            y_notsat = np.nansum(self._weight[idx_y_notsat[0]])
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                idx_X_sat_and_y_notsat = np.where(np.any(self._X[idx_y_notsat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
                X_sat_and_y_notsat = np.nansum(self._weight[idx_X_sat_and_y_notsat[0]])
                noise = X_sat_and_y_notsat / y_notsat * 100
                noise_coalition.append(float(noise))

        return noise_coalition

    
    def key_drivers(self):
        if self._analysis == 'kda':
            kda = self.shapley_values()
            kda_df = pd.DataFrame(kda.items(), columns=['Num', 'Shapley value'])
            kda_df.insert(1, 'Attribute', self._X_varnames)
            kda_df.insert(3, 'Impact (%)', kda_df[['Shapley value']].apply(lambda x: x / x.sum() * 100))
            kda_df.insert(4, 'Impact (base 100)', kda_df[['Shapley value']].apply(lambda x: x / x.mean() * 100))
            kda_df.insert(5,'Dissatisfied on attribute (%)', self.performance_player(kda_df[['Num']]))
            kda_df.insert(6,'%(Dissatisfied on attribute | Dissatisfied Overall)', self.reach_player(kda_df[['Num']]))
            kda_df.insert(7,'%(Dissatisfied on attribute | Not dissatisfied Overall)', self.noise_player(kda_df[['Num']]))
            kda_df.insert(8,'Difference', kda_df['%(Dissatisfied on attribute | Dissatisfied Overall)'] - kda_df['%(Dissatisfied on attribute | Not dissatisfied Overall)'])
            kda_df= kda_df.sort_values(['Shapley value'], ascending=[0])
            kda_df.insert(9, 'Reach', self.reach_coalition(kda_df[['Num']]))
            kda_df.insert(10,'Noise', self.noise_coalition(kda_df[['Num']]))
            kda_df.insert(11,'Objective', kda_df['Reach'] - kda_df['Noise'])
            kda_df = kda_df.reset_index(drop=True)
            
            return kda_df.round(2)
        
        elif self._analysis == 'kea':
            kea = self.shapley_values()
            kea_df = pd.DataFrame(kea.items(), columns=['Num', 'Shapley value'])
            kea_df.insert(1, 'Attribute', self._X_varnames)
            kea_df.insert(3, 'Impact (%)', kea_df[['Shapley value']].apply(lambda x: x / x.sum() * 100))
            kea_df.insert(4, 'Impact (base 100)', kea_df[['Shapley value']].apply(lambda x: x / x.mean() * 100))
            kea_df.insert(5,'Satisfied on attribute (%)', self.performance_player(kea_df[['Num']]))
            kea_df.insert(6,'%(Satisfied on attribute | Satisfied Overall)', self.reach_player(kea_df[['Num']]))
            kea_df.insert(7,'%(Satisfied on attribute | Not Satisfied Overall)', self.noise_player(kea_df[['Num']]))
            kea_df.insert(8,'Difference', kea_df['%(Satisfied on attribute | Satisfied Overall)'] - kea_df['%(Satisfied on attribute | Not Satisfied Overall)'])
            kea_df= kea_df.sort_values(['Shapley value'], ascending=[0])
            kea_df.insert(9, 'Reach', self.reach_coalition(kea_df[['Num']]))
            kea_df.insert(10,'Noise', self.noise_coalition(kea_df[['Num']]))
            kea_df.insert(11,'Objective', kea_df['Reach'] - kea_df['Noise'])
            kea_df = kea_df.reset_index(drop=True)
            
            return kea_df.round(2)
