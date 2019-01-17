import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import globals

def pensions_generator(max_age):

    pension_list = []
    for year in range(globals.start_year, globals.end_year):

        for age in range(max_age+1):

            if year - age < globals.m_basic_state_pension_qual_year:

                pension_list.append(globals.m_adj_basic_state_pension)

            elif age >= globals.inc_qual_age_1_age and year >= globals.inc_qual_age_1_year and year < globals.inc_qual_age_2_year:

                pension_list.append(globals.m_adj_new_state_pension)

            elif year >= globals.inc_qual_age_2_age and year >= globals.inc_qual_age_2_year and year < globals.inc_qual_age_3_year:

                pension_list.append(globals.m_adj_new_state_pension)

            elif age >= globals.inc_qual_age_3_age and year >= globals.inc_qual_age_3_year and year < globals.inc_qual_age_4_year:

                pension_list.append(globals.m_adj_new_state_pension)

            elif age >= globals.inc_qual_age_4_age and year >= globals.inc_qual_age_4_year and year < globals.inc_qual_age_5_year:

                pension_list.append(globals.m_adj_new_state_pension)

            else:

                pension_list.append(0)
                continue


        for age in range(max_age+1):

            if year - age < globals.f_basic_state_pension_qual_year:

                pension_list.append(globals.f_adj_basic_state_pension)

            elif age >= globals.inc_qual_age_1_age and year >= globals.inc_qual_age_1_year and year < globals.inc_qual_age_2_year:

                pension_list.append(globals.f_adj_new_state_pension)

            elif age >= globals.inc_qual_age_2_age and year >= globals.inc_qual_age_2_year and year < globals.inc_qual_age_3_year:

                pension_list.append(globals.f_adj_new_state_pension)

            elif age >= globals.inc_qual_age_3_age and year >= globals.inc_qual_age_3_year and year < globals.inc_qual_age_4_year:

                pension_list.append(globals.f_adj_new_state_pension)

            elif age >= globals.inc_qual_age_4_age and year >= globals.inc_qual_age_4_year and year < globals.inc_qual_age_5_year:

                pension_list.append(globals.f_adj_new_state_pension)

            else:

                pension_list.append(0)
                continue

    return pension_list

def ann_discount_rate(year, discount=globals.DR):

        if discount=='UK Treasury':

            if year <= 30:
                DR = 0.035
            elif year > 30 and year <= 75:
                DR = ((0.035*30) + (0.03*(year-30)))/year
            else:
                DR = ((0.035*30) + (0.03*45) + (0.025*(year-75)))/year

        else:

            DR = discount

        ann_DR = 1/((1+DR)**year)

        return ann_DR

def discount_rate_generator():

    DR_list = []
    for year in range(globals.end_year - globals.start_year):
        DR = ann_discount_rate(year)
        DR_list.append(DR)

    return DR_list

def life_expectancy_generator():

    LE_df = pd.read_csv(globals.proj_path + r'data\\health\\Eng_LE.csv')
    m_LE_list = list(LE_df['male'].values)
    f_LE_list = list(LE_df['female'].values)
    m_f_LE_list = m_LE_list[:globals.econ_age_cap+1] + f_LE_list[:globals.econ_age_cap+1]

    return m_f_LE_list

def wage_loss_calculator(discount):

    wage_loss_df = pd.read_csv(globals.proj_path + r'data\\econ\\lost_wages_input.csv')

    if discount==True:

        m_wages_list = list(wage_loss_df['m_disc'].values)
        f_wages_list = list(wage_loss_df['f_disc'].values)

    else:

        m_wages_list = list(wage_loss_df['m'].values)
        f_wages_list = list(wage_loss_df['f'].values)

    m_f_wages_list = m_wages_list[:globals.econ_age_cap+1] + f_wages_list[:globals.econ_age_cap+1]

    return m_f_wages_list

def calculate_econ_costs(df, discount=True):

    df = df[df.Age <= globals.econ_age_cap ]
    df = df.drop(df[df.Year > globals.end_year].index)

    if discount==True:

        DR_list = discount_rate_generator()

        df['Discount rate'] = np.repeat(DR_list, (globals.econ_age_cap+1)*2)
        df.update(df.iloc[:, 3:7].mul(df['Discount rate'], 0))

    LE_list = life_expectancy_generator()
    df['YLL'] = (LE_list * (globals.end_year - globals.start_year)) * df['c']

    df['QALYs'] = globals.QALY_ihd * df['p']

    df['YLL_cost'] = df['YLL'] * globals.QALY_value
    df['QALY_cost'] = df['QALYs'] * globals.QALY_value

    pension_list = pensions_generator(globals.econ_age_cap)
    df['Pensions'] = pension_list * (df['n'] + df['p'])

    df['treatment costs'] = globals.total_treatment_cost_ppc * df['p']

    df['informal care costs'] = globals.informal_care_ppc * df['p']

    df['morb costs'] = globals.morb_lost_wages_ppc * df['p']

    wage_list = wage_loss_calculator(discount)
    df['wage loss'] = (wage_list * (globals.end_year - globals.start_year)) * df['c']

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
