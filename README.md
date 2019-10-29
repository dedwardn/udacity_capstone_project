# Udacity Data scientist capstone project
This repository has been made to support the blog post produced as a deliverable to the capstone project of the data science nanodegree offered by Udacity.

Starbucks are providing data describing the transactions by a set of users with some features like age, gender and income through a period of time when they were exposed to different types of offers.

The task is described by Udacity as this: 

>Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink or an actual offer such as a discount or BOGO (buy one get one free). Some users might not receive any offer during certain weeks.
>
>Not all users receive the same offer, and that is the challenge to solve with this data set.
>
>Your task is to combine transaction, demographic and offer data to determine which demographic groups respond best to which offer type.

Based on this instruction I framed some research questions as follows: 

- Is there any indication that an offer works?
- Is there any gender which responds better to offers in general?
- Is there any age group which responds better to offers in general?

## Summary 
The short summary is that there is definitely support to claim that offers work. However, the informational ones didn't seem to give much of a spike in spendings for any group. 

It can also seem like women respond better in general with a slightly higher ratio of spending during vs outside of offers. 

There are some indication that the younger and older age groups are more influenced by the offers, but I have not found one group that clearly sticks out. 

## Libraries
- python 3.6
- pandas
- numpy
- matplotlib
- seaborn

and more built standard modules in python 3.6.

## Code structure
The project has been mostly solved in jupyter notebooks. A short explanation is given below. 

Some helper functions has been placed in a separate package called "utils". 

- data: The input data

- Utils: Helper functions
   - plots.py: functions for some self-defined plots
   - cleaning.py: functions to help clean the data after exploration was performed
   - build_matrices.py: Functions to construct matrices according to findings in the exploration and wrangling

- Jupyter notebooks:
   - Starbucks_Capstone_notebook.ipynb - Exploration and wrangling of the input data
   - Build_matrices.ipynb - Investigation of how to build matrices for use in analysis 
   - Heuristics.ipynb - Analysis of data and visualisations. Fairly unstructured due to the exploratory nature of the analysis. 
   
- plots: 
A folder of plots produced for reporting

- offer_df.pkl - dataframe exported by pandas. offers matrix with information about the offers users are given, and some user interaction data. Each row is realted to an offer given to a specific customer. Created in Build_matrices.ipynb
- profile_expanded.pkl - dataframe exported by pandas. Profile expanded is a dataframe with several features engineered from a combination of all the data sets where each row is related to one user. Created in Build_matrices.ipynb
   

## Aknowledgements
I would like to thank my girlfriend for being patient with me during many long nights with this course and in the end capstone project. I would also like to thank the numerous contributors to places like StackExchange. Without you guys, we would be lost all of us! 

