import pandas as pd
import numpy as np
from globals import *



def lifetable(proj_path, gender, IHD_inc, IHD_cf, mort, reduction_scenario=None, f_healthy_arr=None, f_ihd_arr=None):

    pop_df = pd.read_csv(proj_path + "data/population/population.csv")
    ihd_inc_df =  pd.read_csv(proj_path + "data/population/ihd_incidence.csv")
    ihd_mort_df =  pd.read_csv(proj_path + "data/population/ihd_mortality.csv")
    ihd_prev_df =  pd.read_csv(proj_path + "data/population/ihd_prevalence.csv")
    nonihd_mort_df =  pd.read_csv(proj_path + "data/population/nonihd_mortality.csv")


    if gender == 'male':

        pop_arr = pop_df.drop(['Female', 'Age'], axis=1).values
        inc_arr =  ihd_inc_df.drop(['Female', 'Age'], axis=1).values
        ihd_mort_arr =  ihd_mort_df.drop(['Female', 'Age'], axis=1).values
        ihd_prev_arr =  ihd_prev_df.drop(['Female', 'Age'], axis=1).values
        nonihd_mort_arr =  nonihd_mort_df.drop(['Female', 'Age'], axis=1).values

        if f_healthy_arr is None or f_ihd_arr is None:

            print('Note: No births included - births require female lifetable results input')

    elif gender == 'female':

        pop_arr = pop_df.drop(['Male', 'Age'], axis=1).values
        inc_arr =  ihd_inc_df.drop(['Male', 'Age'], axis=1).values
        ihd_mort_arr =  ihd_mort_df.drop(['Male', 'Age'], axis=1).values
        ihd_prev_arr =  ihd_prev_df.drop(['Male', 'Age'], axis=1).values
        nonihd_mort_arr =  nonihd_mort_df.drop(['Male', 'Age'], axis=1).values

    else:

        raise Exception("gender must be 'male' or 'female'")


    if reduction_scenario==None:
        IHD_i_change = 1
        IHD_c_change = 1
        d_change = 1

    else:

        IHD_i_change = 1 / (1 + ((IHD_inc - 1) * (10 - reduction_scenario)))
        IHD_c_change = 1 / (1 + ((IHD_cf - 1) * (10 - reduction_scenario)))
        d_change = 1 / (1 + ((mort - 1) * (10 - reduction_scenario)))


    years = end_year - start_year

    p12 = (inc_arr / (1-ihd_prev_arr))*IHD_i_change
    p12 = np.tile(p12, years)

    p23 = ((ihd_mort_arr/1000000) / ihd_prev_arr)*IHD_c_change
    p23[p23 == np.inf] = 0
    p23 = np.nan_to_num(p23)
    p23 = np.tile(p23, years)


    p24 = np.nan_to_num(((1/2)*(nonihd_mort_arr/1000000) / ihd_prev_arr)*d_change)
    p24[p24 == np.inf] = 0
    p24 = np.nan_to_num(p24)
    p24 = np.tile(p24, years)

    p14 = ((1/2)*(nonihd_mort_arr/1000000) / (1-ihd_prev_arr))*d_change
    p14[p14 == np.inf] = 0
    p14 = np.nan_to_num(p14)
    p14 = np.tile(p14, years)

    p13 = p12*p23
    p13 = np.tile(p13, years)

    state_healthy_arr = np.zeros((max_age, years))
    state_ihd_arr = np.zeros((max_age, years))
    state_inc_arr = np.zeros((max_age, years))
    state_ihd_death_arr = np.zeros((max_age, years))
    state_all_death_arr = np.zeros((max_age, years))


    for i in range(years):

        if i == 0:

            state_healthy_arr[:,i] = (pop_arr[:,i] - (ihd_prev_arr[:,i] * pop_arr[:,i]))
            state_ihd_arr[:,i] = ihd_prev_arr[:,i] * pop_arr[:,i]

        else:

            for age in range(1, max_age):

                state_healthy_arr[age,i] = state_healthy_arr[age-1,i-1]  - (state_healthy_arr[age-1,i-1]*(p12[age,i] + p13[age,i] + p14[age,i]))
                state_ihd_arr[age,i] = state_ihd_arr[age-1, i-1] + (state_healthy_arr[age-1,i-1]*p12[age,i]) - (state_ihd_arr[age-1,i-1]*(p23[age,i] + p24[age,i]))
                state_inc_arr[age,i] = (state_healthy_arr[age-1,i-1]*p12[age,i])
                state_ihd_death_arr[age,i] = (state_healthy_arr[age-1,i-1]*p13[age,i]) + state_ihd_arr[age-1,i-1]*p23[age,i]
                state_all_death_arr[age,i] = (state_healthy_arr[age-1,i-1]*p14[age,i]) + state_ihd_arr[age-1,i-1]*p24[age,i]

            if gender == 'female':

                state_healthy_arr[0, i] = (sum(state_healthy_arr[16:45,i-1]) + sum(state_ihd_arr[16:45,i-1]))* 61 / 1000 / 2

            elif f_healthy_arr is not None and f_ihd_arr is not None:

                state_healthy_arr[0, i] = (sum(f_healthy_arr[16:45,i-1]) + sum(f_ihd_arr[16:45,i-1]))* 61 / 1000 / 2

            else:

                continue


    return state_healthy_arr, state_inc_arr, state_ihd_arr, state_ihd_death_arr, state_all_death_arr



def difference(base_df, burd_df):

    base_counts_df = base_df[['n', 'i', 'p', 'c', 'd']].copy()
    burd_counts_df = burd_df[['n', 'i', 'p', 'c', 'd']].copy()
    year_sex_df =  base_df[['Gender', 'Age', 'Year']].copy()

    diff_df = base_counts_df - burd_counts_df

    diff_df = year_sex_df.join(diff_df, how='outer')

    return diff_df


def lifetable_results_to_dataframe(gender, lifetable_results_list):

    df = pd.DataFrame(
        {'Gender': [gender]*((end_year - start_year)*max_age),
         'Age': list(range(max_age))*(end_year - start_year),
         'Year': np.repeat(list(range(start_year,end_year)), max_age),
         'n': np.round(lifetable_results_list[0].flatten('F'), decimals=1),
         'i': np.round(lifetable_results_list[1].flatten('F'), decimals=1),
         'p': np.round(lifetable_results_list[2].flatten('F'), decimals=1),
         'c': np.round(lifetable_results_list[3].flatten('F'), decimals=1),
         'd': np.round(lifetable_results_list[4].flatten('F'), decimals=1)
           })

    return df
