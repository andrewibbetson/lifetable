import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from globals import *


def calculate_econ_costs(df, discount=True):

    age_cap = 100
    df = df[df.Age <= age_cap ]

    if discount==True:

        DR_list = []
        for year in range(end_year - start_year):
            DR = ann_discount_rate(year)
            DR_list.append(DR)

        df['Discount rate'] = np.repeat(DR_list, (age_cap+1)*2)

        df.update(df.iloc[:, 3:7].mul(df['Discount rate'], 0))

    df = df.drop(df[df.Year > end_year].index)


    LE_df = pd.read_csv(proj_path + r'data\\health\\Eng_LE.csv')
    m_LE_list = list(LE_df['male'].values)
    f_LE_list = list(LE_df['female'].values)
    m_f_LE_list = m_LE_list[:age_cap+1] + f_LE_list[:age_cap+1]
    df['YLL'] = (m_f_LE_list * (end_year - start_year)) * df['c']

    df['QALYs'] = QALY_ihd * df['p']

    df['YLL_cost'] = df['YLL'] * QALY_value
    df['QALY_cost'] = df['QALYs'] * QALY_value

    pension_list = pensions_generator(age_cap, start_year, end_year)
    df['Pensions'] = pension_list * (df['n'] + df['p'])

    df['treatment costs'] = total_treatment_cost_ppc * df['p']

    df['informal care costs'] = informal_care_ppc * df['p']

    df['morb costs'] = morb_lost_wages_ppc * df['p']

    wage_loss_df = pd.read_csv(proj_path + r'data\\econ\\lost_wages_input.csv')

    if discount==True:

        m_wages_list = list(wage_loss_df['m_disc'].values)
        f_wages_list = list(wage_loss_df['f_disc'].values)

    else:

        m_wages_list = list(wage_loss_df['m'].values)
        f_wages_list = list(wage_loss_df['f'].values)

    m_f_wages_list = m_wages_list[:age_cap+1] + f_wages_list[:age_cap+1]
    df['wage loss'] = (m_f_wages_list * (end_year - start_year)) * df['c']

    return df


def totals(df):

        df.drop(['Gender','Age','n','p','i','c','d','YLL','QALYs'], axis=1, inplace = True)

        if 'Discount rate' in df.columns:

            df.drop(['Discount rate'], axis=1, inplace = True)

        df = df.groupby("Year").sum()

        '''df.plot()
        #print(df.head())
        plt.title('Total Change in IHD-related costs over time - Discounted')
        plt.show()'''

        totals_dict = {}
        for column in df:

            totals_dict.update({column: df[column].sum()/1000000000})

        return totals_dict
