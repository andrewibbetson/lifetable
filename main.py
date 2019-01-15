from globals import *
from lifetable import *
from econ import *
import pandas as pd
import numpy as np


def run_lifetable(IHD_inc=IHD_inc, IHD_cf=IHD_cf, mort=mort, reduction_scenario=None):

    f_lifetable_results_list = lifetable(proj_path, 'female', IHD_inc, IHD_cf, mort, reduction_scenario)
    m_lifetable_results_list = lifetable(proj_path, 'male', IHD_inc, IHD_cf, mort, reduction_scenario, f_healthy_arr=f_lifetable_results_list[0], f_ihd_arr=f_lifetable_results_list[2])

    f_lifetable_df = lifetable_results_to_dataframe('female', f_lifetable_results_list)
    m_lifetable_df = lifetable_results_to_dataframe('male', m_lifetable_results_list)

    m_f_lifetable_df = pd.concat([m_lifetable_df, f_lifetable_df])
    sorted_m_f_lifetable_df = m_f_lifetable_df.sort_values(['Year', 'Gender', 'Age'], ascending=[1,0,1])
    sorted_m_f_lifetable_df = sorted_m_f_lifetable_df.reset_index(drop=True)

    return sorted_m_f_lifetable_df


def run_prob_sens(runs):

    base_lifetable_df = run_lifetable(IHD_inc, IHD_cf, mort, baseline)

    #diff_econ_totals_list = []
    disease_state_totals_list = []
    for run in range(runs):

        print('sens run: ' + str(run))

        mu, sigma = IHD_inc, ((IHD_inc_ub - IHD_inc_lb) / 2.78)
        IHD_inc_sample = np.random.normal(mu, sigma)

        # IHD cf
        # mean and standard deviation
        mu, sigma = IHD_cf, ((IHD_cf_ub - IHD_cf_lb) / 2.78)
        IHD_cf_sample = np.random.normal(mu, sigma)

        # mort
        # mean and standard deviation
        mu, sigma = mort, ((mort_ub - mort_lb) / 2.78)
        mort_sample = np.random.normal(mu, sigma)

        sens_run_df = run_lifetable(IHD_inc_sample, IHD_cf_sample, mort_sample, reduction_scenario_anth)

        diff_df = difference(base_lifetable_df, sens_run_df)

        df = diff_df.copy()
        df.drop(['Gender','Age'], axis=1, inplace = True)
        df = df.groupby("Year").sum()

        #diff_econ_results = econ(diff_df)
        #diff_econ_totals = totals(diff_econ_results)

        #diff_econ_totals_list.append(diff_econ_totals)

        disease_state_totals_list.append(df)

    #sens_df = pd.DataFrame(diff_econ_totals_list)
    df = pd.concat(disease_state_totals_list, axis=1)
    sens_df = pd.DataFrame(df)

    return sens_df


sens_df = run_prob_sens(1000)
#sens_df.to_csv(proj_path + '/outputs/' + 'sens_disease_state_results.csv')



'''multi_way_list = []
params = [[IHD_inc_ub, IHD_cf_ub], [IHD_inc_lb, IHD_cf_lb], [IHD_inc_ub, IHD_cf_lb], [IHD_inc_lb, IHD_cf_ub]]

for run in range(4):

    IHD_inc = params[run][0]
    IHD_cf = params[run][1]

    df_base = run_lifetable(IHD_inc, IHD_cf, mort, baseline)
    df_anth = run_lifetable(IHD_inc, IHD_cf, mort, reduction_scenario_anth)
    diff_df = difference(df_anth, df_base)

    base_econ_results = econ(df_base)
    anth_econ_results = econ(df_anth)
    diff_econ_results = econ(diff_df)

    base_econ_totals = totals(base_econ_results)
    anth_econ_totals = totals(anth_econ_results)
    diff_econ_totals = totals(diff_econ_results)


    multi_way_list.append(diff_econ_totals)
    multi_way_list.append(base_econ_totals)
    multi_way_list.append(anth_econ_totals)


multi_df = pd.DataFrame(multi_way_list)
multi_df.to_csv(proj_path + '/outputs/' + 'multi_sens_econ_results.csv')'''
