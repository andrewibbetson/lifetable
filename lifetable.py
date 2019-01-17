import pandas as pd
import numpy as np
import globals

class Lifetable():

    def __init__(self, inc=globals.IHD_inc, cf=globals.IHD_cf, non_dis_mort=globals.non_IHD_mort, reduction_scenario=None):

        self.pop_df = read_population_data()

        self.inc_df =  read_incidence_data()
        self.dis_mort_df =  read_disease_mortality_data()
        self.prev_df =  read_prevalence_data()
        self.non_dis_mort_df =  read_non_disease_mortality_data()

        self.time_horizon = globals.end_year - globals.start_year
        self.max_age = globals.max_age

        self.RR_inc = inc
        self.RR_cf = cf
        self.RR_mort = non_dis_mort

        self.reduction_scenario = reduction_scenario


    def run_lifetable(self):

        m_pop_arr = gender_select(self.pop_df, 'male')
        m_inc_arr =  gender_select(self.inc_df, 'male')
        m_dis_mort_arr =  gender_select(self.dis_mort_df, 'male')
        m_prev_arr =  gender_select(self.prev_df, 'male')
        m_non_dis_mort_arr =  gender_select(self.non_dis_mort_df, 'male')

        f_pop_arr = gender_select(self.pop_df, 'female')
        f_inc_arr =  gender_select(self.inc_df, 'female')
        f_dis_mort_arr =  gender_select(self.dis_mort_df, 'female')
        f_prev_arr =  gender_select(self.prev_df, 'female')
        f_non_dis_mort_arr =  gender_select(self.non_dis_mort_df, 'female')

        m_state_healthy_arr = np.zeros((self.max_age, self.time_horizon))
        m_state_prev_arr = np.zeros((self.max_age, self.time_horizon))
        m_state_inc_arr = np.zeros((self.max_age, self.time_horizon))
        m_state_dis_death_arr = np.zeros((self.max_age, self.time_horizon))
        m_state_all_death_arr = np.zeros((self.max_age, self.time_horizon))

        f_state_healthy_arr = np.zeros((self.max_age, self.time_horizon))
        f_state_prev_arr = np.zeros((self.max_age, self.time_horizon))
        f_state_inc_arr = np.zeros((self.max_age, self.time_horizon))
        f_state_dis_death_arr = np.zeros((self.max_age, self.time_horizon))
        f_state_all_death_arr = np.zeros((self.max_age, self.time_horizon))

        inc_multiplier = calc_risk_multiplier(self.RR_inc, self.reduction_scenario)
        cf_multiplier = calc_risk_multiplier(self.RR_cf, self.reduction_scenario)
        non_dis_mort_multiplier = calc_risk_multiplier(self.RR_mort, self.reduction_scenario)

        m_p12_arr = calculate_p12(m_inc_arr, m_prev_arr, inc_multiplier, self.time_horizon)
        m_p14_arr = calculate_p14(m_non_dis_mort_arr, m_prev_arr, non_dis_mort_multiplier, self.time_horizon)
        m_p23_arr = calculate_p23(m_dis_mort_arr, m_prev_arr, cf_multiplier, self.time_horizon)
        m_p24_arr = calculate_p24(m_non_dis_mort_arr, m_prev_arr, non_dis_mort_multiplier, self.time_horizon)
        m_p13_arr = calculate_p13(m_p12_arr, m_p23_arr, self.time_horizon)

        f_p12_arr = calculate_p12(f_inc_arr, f_prev_arr, inc_multiplier, self.time_horizon)
        f_p14_arr = calculate_p14(f_non_dis_mort_arr, f_prev_arr, non_dis_mort_multiplier, self.time_horizon)
        f_p23_arr = calculate_p23(f_dis_mort_arr, f_prev_arr, cf_multiplier, self.time_horizon)
        f_p24_arr = calculate_p24(f_non_dis_mort_arr, f_prev_arr, non_dis_mort_multiplier, self.time_horizon)
        f_p13_arr = calculate_p13(f_p12_arr, f_p23_arr, self.time_horizon)

        for i in range(self.time_horizon):

            if i == 0:

                m_state_healthy_arr[:,i] = (m_pop_arr[:,i] - (m_prev_arr[:,i] * m_pop_arr[:,i]))
                m_state_prev_arr[:,i] = m_prev_arr[:,i] * m_pop_arr[:,i]

                f_state_healthy_arr[:,i] = (f_pop_arr[:,i] - (f_prev_arr[:,i] * f_pop_arr[:,i]))
                f_state_prev_arr[:,i] = f_prev_arr[:,i] * f_pop_arr[:,i]

            else:

                for age in range(1, self.max_age):

                    m_state_healthy_arr[age,i] = m_state_healthy_arr[age-1,i-1]  - (m_state_healthy_arr[age-1,i-1]*(m_p12_arr[age,i] + m_p13_arr[age,i] + m_p14_arr[age,i]))
                    m_state_prev_arr[age,i] = m_state_prev_arr[age-1, i-1] + (m_state_healthy_arr[age-1,i-1]*m_p12_arr[age,i]) - (m_state_prev_arr[age-1,i-1]*(m_p23_arr[age,i] + m_p24_arr[age,i]))
                    m_state_inc_arr[age,i] = (m_state_healthy_arr[age-1,i-1]*m_p12_arr[age,i])
                    m_state_dis_death_arr[age,i] = (m_state_healthy_arr[age-1,i-1]*m_p13_arr[age,i]) + m_state_prev_arr[age-1,i-1]*m_p23_arr[age,i]
                    m_state_all_death_arr[age,i] = (m_state_healthy_arr[age-1,i-1]*m_p14_arr[age,i]) + m_state_prev_arr[age-1,i-1]*m_p24_arr[age,i]

                    f_state_healthy_arr[age,i] = f_state_healthy_arr[age-1,i-1]  - (f_state_healthy_arr[age-1,i-1]*(f_p12_arr[age,i] + f_p13_arr[age,i] + f_p14_arr[age,i]))
                    f_state_prev_arr[age,i] = f_state_prev_arr[age-1, i-1] + (f_state_healthy_arr[age-1,i-1]*f_p12_arr[age,i]) - (f_state_prev_arr[age-1,i-1]*(f_p23_arr[age,i] + f_p24_arr[age,i]))
                    f_state_inc_arr[age,i] = (f_state_healthy_arr[age-1,i-1]*f_p12_arr[age,i])
                    f_state_dis_death_arr[age,i] = (f_state_healthy_arr[age-1,i-1]*f_p13_arr[age,i]) + f_state_prev_arr[age-1,i-1]*f_p23_arr[age,i]
                    f_state_all_death_arr[age,i] = (f_state_healthy_arr[age-1,i-1]*f_p14_arr[age,i]) + f_state_prev_arr[age-1,i-1]*f_p24_arr[age,i]

                    m_state_healthy_arr[0, i] = (sum(f_state_healthy_arr[16:45,i-1]) + sum(f_state_prev_arr[16:45,i-1]))* 61 / 1000 / 2
                    f_state_healthy_arr[0, i] = (sum(f_state_healthy_arr[16:45,i-1]) + sum(f_state_prev_arr[16:45,i-1]))* 61 / 1000 / 2

            m_results = [m_state_healthy_arr, m_state_inc_arr, m_state_prev_arr, m_state_dis_death_arr, m_state_all_death_arr]
            f_results = [f_state_healthy_arr, f_state_inc_arr, f_state_prev_arr, f_state_dis_death_arr, f_state_all_death_arr]

        result = process_lt_results(m_results, f_results)

        return result

def calculate_p12(inc_arr, prev_arr, inc_multiplier, time_horizon):

    p12_series = (inc_arr / (1-prev_arr))*inc_multiplier
    p12_arr = np.tile(p12_series, time_horizon)

    return p12_arr

def calculate_p13(p12, p23, time_horizon):

    p13_series = p12*p23
    p13_arr = np.tile(p13_series, time_horizon)

    return p13_arr

def calculate_p14(non_dis_mort_arr, prev_arr, non_dis_mort_multiplier, time_horizon):

    p14_series = ((1/2)*(non_dis_mort_arr/1000000) / (1-prev_arr))*non_dis_mort_multiplier
    p14_series[p14_series == np.inf] = 0
    p14_series = np.nan_to_num(p14_series)
    p14_arr = np.tile(p14_series, time_horizon)

    return p14_arr

def calculate_p23(dis_mort_arr, prev_arr, cf_multiplier, time_horizon):

    p23_series = ((dis_mort_arr/1000000) / prev_arr)*cf_multiplier
    p23_series[p23_series == np.inf] = 0
    p23_series = np.nan_to_num(p23_series)
    p23_arr = np.tile(p23_series, time_horizon)

    return p23_arr

def calculate_p24(non_dis_mort_arr, prev_arr, non_dis_mort_multiplier, time_horizon):

    p24_series = np.nan_to_num(((1/2)*(non_dis_mort_arr/1000000) / prev_arr)*non_dis_mort_multiplier)
    p24_series[p24_series == np.inf] = 0
    p24_series = np.nan_to_num(p24_series)
    p24_arr = np.tile(p24_series, time_horizon)

    return p24_arr

def read_population_data():
    pop_df = pd.read_csv(globals.proj_path + "data/population/population.csv")
    return pop_df

def read_incidence_data():
    inc_df =  pd.read_csv(globals.proj_path + "data/population/ihd_incidence.csv")
    return inc_df

def read_disease_mortality_data():
    mort_df =  pd.read_csv(globals.proj_path + "data/population/ihd_mortality.csv")
    return mort_df

def read_prevalence_data():
    prev_df =  pd.read_csv(globals.proj_path + "data/population/ihd_prevalence.csv")
    return prev_df

def read_non_disease_mortality_data():
    non_dis_mort_df =  pd.read_csv(globals.proj_path + "data/population/nonihd_mortality.csv")
    return non_dis_mort_df

def gender_select(df, gender):

    if gender == 'male':
        arr = df.drop(['Female', 'Age'], axis=1).values

    elif gender == 'female':
        arr = df.drop(['Male', 'Age'], axis=1).values

    else:
        raise Exception("gender must be 'male' or 'female'")

    return arr

def calc_risk_multiplier(RR, reduction_scenario):

    if reduction_scenario==None:
        risk_multiplier = 1

    else:
        risk_multiplier = 1 / (1 + ((RR - 1) * (10 - reduction_scenario)))

    return risk_multiplier

def lifetable_results_to_dataframe(gender, lifetable_results_list):

    df = pd.DataFrame(
        {'Gender': [gender]*((globals.end_year - globals.start_year)*globals.max_age),
         'Age': list(range(globals.max_age))*(globals.end_year - globals.start_year),
         'Year': np.repeat(list(range(globals.start_year, globals.end_year)), globals.max_age),
         'n': np.round(lifetable_results_list[0].flatten('F'), decimals=1),
         'i': np.round(lifetable_results_list[1].flatten('F'), decimals=1),
         'p': np.round(lifetable_results_list[2].flatten('F'), decimals=1),
         'c': np.round(lifetable_results_list[3].flatten('F'), decimals=1),
         'd': np.round(lifetable_results_list[4].flatten('F'), decimals=1)
           })

    return df

def process_lt_results(m_results, f_results):

    m_lifetable_results_list = m_results
    f_lifetable_results_list = f_results

    f_lifetable_df = lifetable_results_to_dataframe('female', f_lifetable_results_list)
    m_lifetable_df = lifetable_results_to_dataframe('male', m_lifetable_results_list)

    m_f_lifetable_df = pd.concat([m_lifetable_df, f_lifetable_df])

    sorted_m_f_lifetable_df = m_f_lifetable_df.sort_values(['Year', 'Gender', 'Age'], ascending=[1,0,1])

    sorted_m_f_lifetable_df = sorted_m_f_lifetable_df.reset_index(drop=True)

    return sorted_m_f_lifetable_df

def difference(base_df, burd_df):

    base_counts_df = base_df[['n', 'i', 'p', 'c', 'd']].copy()
    burd_counts_df = burd_df[['n', 'i', 'p', 'c', 'd']].copy()
    year_sex_df =  base_df[['Gender', 'Age', 'Year']].copy()

    diff_df = base_counts_df - burd_counts_df

    diff_df = year_sex_df.join(diff_df, how='outer')

    return diff_df
