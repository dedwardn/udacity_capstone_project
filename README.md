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