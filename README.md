# lifetable
A lifetable for modelling health outcomes. 

The lifetable has initially been set up to model the impact of PM2.5 reduction scenarios on ischemic heart disease morbidity and 
mortality in the UK. 

It also features an econ.py module which allows health-related costs to be estimated. These include those relating to treatment, 
state pensions, productivity and the monetisation of loss of life and disability.

The main model parameters are stored in the globals.py module for ease of input.

Functions in the main.py module allow users to run both determinstic and probablistic models. Currently, probability distributions have
only been assigned to the transition rate multipliers associated with PM2.5 exposure. 
