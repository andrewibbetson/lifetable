# GLOBAL VARS

#proj_path = r'H:\\My Documents\\COMEAP\\econ\\'
proj_path = r'C:\\Users\\andre\\OneDrive\\Documents\\LSHTM\\COMEAP\\econ\\'

# Time horizon
start_year = 2017
time_horizon = 50
end_year = start_year + time_horizon
max_age = 106

# QALYs
# using a value of 0.7591 (SE: 0.0122) from Stevanovic et al. 2016
# QALY value in accordance with NICE Guidelines
QALY_ihd = 0.7591
QALY_value = 30000

# Pensions
# OBR pension age forecasts (FSR report)
# 2020: 66; 2028: 67; 2039: 68; 2054: 69; 2068 = 70
# triple lock - penison increases with CPI, average earnings or 2.5%
# maybe assume 2.5% per year increase for now
basic_state_pension = 125.95 * 52
new_state_pension = 164.35 * 52

m_basic_state_pension_qual_year = 1951
f_basic_state_pension_qual_year = 1953

inc_qual_age_1_year = 2020
inc_qual_age_1_age = 66
inc_qual_age_2_year = 2028
inc_qual_age_2_age = 67
inc_qual_age_3_year = 2039
inc_qual_age_3_age = 68
inc_qual_age_4_year = 2054
inc_qual_age_4_age = 69
inc_qual_age_5_year = 2068
inc_qual_age_5_age = 70

# need to adjust for employment - male/female
# use historical employment rate?

m_emp_rate_2018 = 0.8
f_emp_rate_2018 = 0.711

m_adj_basic_state_pension = basic_state_pension * m_emp_rate_2018
m_adj_new_state_pension = new_state_pension * m_emp_rate_2018
f_adj_basic_state_pension = basic_state_pension * f_emp_rate_2018
f_adj_new_state_pension = new_state_pension * f_emp_rate_2018

# healthcare
# top-down approach
# data from European Heart Network (EHN) - costs per prevalent case (ppc)
primary_care = 51
outpatient_care = 103
AnE = 35
inpatient_care = 424
medications = 130
total_treatment_cost_ppc = primary_care + outpatient_care + AnE + inpatient_care + medications

# informal care
informal_care_ppc = 881

#lost wages from morbidity (sick days)
morb_lost_wages_ppc = 329

# Relative risk estimates for 10µg increase in PM2.5
IHD_inc = 1.10
IHD_cf = 1.28
non_IHD_mort = 1.11

# 95% confidence intervals

IHD_inc_lb = 1.04
IHD_inc_ub = 1.15

IHD_cf_lb = 1.16
IHD_cf_ub = 1.41

mort_lb = 1.10
mort_ub = 1.12

# scenarios

reduction_scenario_anth = 8.71
reduction_scenario_1 = 1
baseline = None

# discounting

DR = 0.035

# econ age cap

econ_age_cap = 100
