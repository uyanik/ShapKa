# -*- coding: utf-8 -*-
"""
This module compute the kano model with shapley values allocation
"""

import numpy as np
import pandas as pd
from shapleykano.cooperativegame import Game
from shapleykano.payoff import Payoff
np.warnings.filterwarnings('ignore')

class KanoModel(object):
    """
    Description
    """
    def __init__(self, df,
                 y_varname, X_varnames,
                 analysis,
                 y_dissat_upperbound, y_sat_lowerbound,
                 X_dissat_upperbound, X_sat_lowerbound):
        self._df = df
        self._y_varname  = y_varname
        self._X_varnames = X_varnames
        self._y = self._df[self._y_varname].values
        self._X = self._df[self._X_varnames].values
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
                    self._X_dissat_upperbound, self._X_sat_lowerbound)

        characteristic_function = game.CharacteristicFunction(self._analysis)

        payoff = Payoff(characteristic_function)

        shapley_values = payoff.shapley_value()

        return shapley_values


    def reach_player(self, idx_player):

        if self._analysis == 'kda':
            idx_dissat = np.where(self._y <= self._y_dissat_upperbound)
            y_dissat = sum(self._y <= self._y_dissat_upperbound)
            X_dissat_and_y_dissat = sum(np.any(self._X[idx_dissat[0]][:, [idx_player]] <= self._X_dissat_upperbound, axis=1))
            reach_player = X_dissat_and_y_dissat / y_dissat * 100

        elif self._analysis == 'kea':
            idx_sat = np.where(self._y >= self._y_sat_lowerbound)
            y_sat = sum(self._y >= self._y_sat_lowerbound)
            X_sat_and_y_sat = sum(np.any(self._X[idx_sat[0]][:, [idx_player]] >= self._X_sat_lowerbound, axis=1))
            reach_player = X_sat_and_y_sat / y_sat * 100

        return reach_player


    def noise_player(self, idx_player):

        if self._analysis == 'kda':
            idx_notdissat = np.where(self._y > self._y_dissat_upperbound)
            y_notdissat = sum(self._y > self._y_dissat_upperbound)
            X_dissat_and_y_notdissat = sum(np.any(self._X[idx_notdissat[0]][:, [idx_player]] <= self._X_dissat_upperbound, axis=1))
            noise_player = X_dissat_and_y_notdissat / y_notdissat * 100

        elif self._analysis == 'kea':
            idx_notsat = np.where(self._y < self._y_sat_lowerbound)
            y_notsat = sum(self._y < self._y_sat_lowerbound)
            X_sat_and_y_notsat = sum(np.any(self._X[idx_notsat[0]][:,[idx_player]] >= self._X_sat_lowerbound, axis=1))
            noise_player = X_sat_and_y_notsat / y_notsat * 100

        return noise_player


    def reach_coalition(self, ranking_players):

        if self._analysis == 'kda':
            coalition = []
            reach_coalition = []
            idx_dissat = np.where(self._y <= self._y_dissat_upperbound)
            y_dissat = sum(self._y <= self._y_dissat_upperbound)
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                X_dissat_and_y_dissat = sum(np.any(self._X[idx_dissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
                reach = X_dissat_and_y_dissat / y_dissat * 100
                reach_coalition.append(float(reach))

        elif self._analysis == 'kea':
            coalition = []
            reach_coalition = []
            idx_sat = np.where(self._y >= self._y_sat_lowerbound)
            y_sat = sum(self._y >= self._y_sat_lowerbound)
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                X_sat_and_y_sat = sum(np.any(self._X[idx_sat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
                reach = X_sat_and_y_sat / y_sat * 100
                reach_coalition.append(float(reach))

        return reach_coalition


    def noise_coalition(self, ranking_players):
        coalition = []
        noise_coalition = []

        if self._analysis == 'kda':
            idx_notdissat = np.where(self._y > self._y_dissat_upperbound)
            y_notdissat = sum(self._y > self._y_dissat_upperbound)
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                X_dissat_and_y_notdissat = sum(np.any(self._X[idx_notdissat[0]][:, coalition] <= self._X_dissat_upperbound, axis=1))
                noise = X_dissat_and_y_notdissat / y_notdissat * 100
                noise_coalition.append(float(noise))

        elif self._analysis == 'kea':
            idx_notsat = np.where(self._y < self._y_sat_lowerbound)
            y_notsat = sum(self._y < self._y_sat_lowerbound)
            for (index_label, row_series) in ranking_players.iterrows():
                coalition.append(index_label)
                X_sat_and_y_notsat = sum(np.any(self._X[idx_notsat[0]][:, coalition] >= self._X_sat_lowerbound, axis=1))
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
            kda_df.insert(5,'Dissatisfied on attribute (%)', kda_df[['Num']].apply(lambda x: sum(self._X[:, x] <= self._X_dissat_upperbound) / len(self._X[:, x]) * 100))
            kda_df.insert(6,'%(Dissatisfied on attribute | Dissatisfied Overall)', kda_df[['Num']].apply(lambda x: self.reach_player(x)))
            kda_df.insert(7,'%(Dissatisfied on attribute | Not dissatisfied Overall)', kda_df[['Num']].apply(lambda x: self.noise_player(x)))
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
            kea_df.insert(5,'Satisfied on attribute (%)', kea_df[['Num']].apply(lambda x: sum(self._X[:, x] >= self._X_sat_lowerbound) / len(self._X[:, x]) * 100))
            kea_df.insert(6,'%(Satisfied on attribute | Satisfied Overall)', kea_df[['Num']].apply(lambda x: self.reach_player(x)))
            kea_df.insert(7,'%(Satisfied on attribute | Not Satisfied Overall)', kea_df[['Num']].apply(lambda x: self.noise_player(x)))
            kea_df.insert(8,'Difference', kea_df['%(Satisfied on attribute | Satisfied Overall)'] - kea_df['%(Satisfied on attribute | Not Satisfied Overall)'])
            kea_df= kea_df.sort_values(['Shapley value'], ascending=[0])
            kea_df.insert(9, 'Reach', self.reach_coalition(kea_df[['Num']]))
            kea_df.insert(10,'Noise', self.noise_coalition(kea_df[['Num']]))
            kea_df.insert(11,'Objective', kea_df['Reach'] - kea_df['Noise'])
            kea_df = kea_df.reset_index(drop=True)
            return kea_df.round(2)
