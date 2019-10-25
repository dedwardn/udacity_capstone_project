import pandas as pd
import numpy as np

def clean_portfolio(df):
    """
    Cleans and imputes the portfolio dataframe according to findings in exploratory analysis
    :param df: raw data portfolio dataframe
    :return: pd.Dataframe
    """
    # Get all unique channels
    channels = np.unique([channel for chans in df['channels'].items() for channel in chans[1]])
    # Create dummy values for channels
    portfolio_clean = df.copy(deep=True)  # To keep the original dataset, we copy the df
    for channel in channels:
        portfolio_clean["channel_" + channel] = portfolio['channels'].apply(lambda l: 1 if channel in l else 0)
    portfolio_clean.drop(columns='channels', inplace=True)
    # Create dummy values for offer_type
    type_dummies = pd.get_dummies(df['offer_type'], prefix='type', prefix_sep='_')
    df = pd.concat((df, type_dummies), axis=1, sort=False)

    return df

def clean_profile_data(df):
    df['became_member_on'] = pd.to_datetime(df['became_member_on'], format="%Y%m%d")
    return df

