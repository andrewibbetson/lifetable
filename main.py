import globals
import lifetable as lt
from econ import calculate_econ_costs, totals
import pandas as pd
import numpy as np


def base_lifetable():

    lifetable = lt.Lifetable(globals.IHD_inc, globals.IHD_cf, globals.non_IHD_mort, globals.baseline)
    lifetable_result_df = lifetable.run_lifetable()

    return lifetable_result_df

def prob_sens(runs, econ=False):

    base_lifetable = lt.Lifetable(globals.IHD_inc, globals.IHD_cf, globals.non_IHD_mort, globals.baseline)
    base_lifetable_result_df = base_lifetable.run_lifetable()

    diff_econ_totals_list = []
    disease_state_totals_list = []
    for run in range(runs):

        print('sens run: ' + str(run))

        mu, sigma = globals.IHD_inc, ((globals.IHD_inc_ub - globals.IHD_inc_lb) / 2.78)
        IHD_inc_s = np.random.normal(mu, sigma)

        mu, sigma = globals.IHD_cf, ((globals.IHD_cf_ub - globals.IHD_cf_lb) / 2.78)
        IHD_cf_s = np.random.normal(mu, sigma)

        mu, sigma = globals.non_IHD_mort, ((globals.mort_ub - globals.mort_lb) / 2.78)
        mort_s = np.random.normal(mu, sigma)

        sens_lifetable = lt.Lifetable(IHD_inc_s, IHD_cf_s, mort_s, globals.reduction_scenario_anth)
        sens_lifetable_result_df = sens_lifetable.run_lifetable()

        diff_df = lt.difference(base_lifetable_result_df, sens_lifetable_result_df)

        df = diff_df.copy()

        if econ==False:

            df.drop(['Gender','Age'], axis=1, inplace = True)
            df = df.groupby("Year").sum()
            disease_state_totals_list.append(df)

        else:

            diff_econ_results = calculate_econ_costs(df)
            diff_econ_totals = totals(diff_econ_results)
            diff_econ_totals_list.append(diff_econ_totals)

    if econ==False:

        df = pd.concat(disease_state_totals_list, axis=1)
        sens_df = pd.DataFrame(df)

    else:

        sens_df = pd.DataFrame(diff_econ_totals_list)

    return sens_df

sens_df = prob_sens(10, True)
sens_df.to_csv(globals.proj_path + '/outputs/' + 'sens_disease_state_results_test_econ.csv')


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
