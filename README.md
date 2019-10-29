# Udacity Data scientist capstone project
This repository has been made to support the blog post produced as a deliverable to the capstone project of the data science nanodegree offered by Udacity.

Starbucks are providing data describing the transactions by a set of users with some features like age, gender and income through a period of time when they were exposed to different types of offers.

The task is described by Udacity as this: 

>Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink or an actual offer such as a discount or BOGO (buy one get one free). Some users might not receive any offer during certain weeks.
>
>Not all users receive the same offer, and that is the challenge to solve with this data set.
>
>Your task is to combine transaction, demographic and offer data to determine which demographic groups respond best to which offer type.

## Libraries
- python 3.6
- pandas
- numpy
- matplotlib
- seaborn

and more built standard modules in python 3.6.

## 


# Build matrices notebooks
This notebook is used to develop the matrices that will be used for analysis. Based on learnings from the exploratory notebook "Starbucks_Capstone_notebook.ipynb". I have defined a set of parameteres that has to be derived from the combination of portfolio, profile and transcript data. 

## Interaction matrices
In princple I have decided to make two main matrices. One focusing on the users, and one focusing on the offers given. 

Documentation of the columns for each matrix is given in a separate description. XXINSERT_REF

### Offer based interactions
The offers dataframe will have one line per offer given to a user. Each line will consist of data related to the offer, taken from the portfolio data, data related to user identity, taken from the profile data, and data related to user interactions with the given offer, derived from the transcript data. This matrix will be the basis for investigating the user - offer interactions. 

### User based interactions
The profile_exp dataframe will be built with one row per user (in principle an expansion of the profile.json data. The expansion will provide features about the user, user details as provided in the original profile data, and aggregated features about the users offer and spending history. This matrix will be used for segmentation analysis of the users and their interactions. 

## Info
The functions created in this notebook will be moved to different python modules as seen fit. There are a lot of helper methods needed to build both matrices, and these can be investigated in detail below, or in the 