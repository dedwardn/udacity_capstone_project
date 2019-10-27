import pandas as pd
import numpy as np

def clean_portfolio(df):
    """
    Cleans and imputes the portfolio dataframe according to findings in exploratory analysis
    :type df: pd.DataFrame
    :param df: raw data portfolio dataframe
    :return: pd.Dataframe
    """
    df = df.copy(deep=True)
    # Get all unique channels
    channels = np.unique([channel for chans in df['channels'].items() for channel in chans[1]])
    # Create dummy values for channels
    for channel in channels:
        df["channel_" + channel] = df['channels'].apply(lambda l: 1 if channel in l else 0)
    df = df.drop(columns='channels')
    # Create dummy values for offer_type
    type_dummies = pd.get_dummies(df['offer_type'], prefix='type', prefix_sep='_')
    df = pd.concat((df, type_dummies), axis=1, sort=False)
    return df

def clean_profile_data(df):
    """
        :type df: pd.DataFrame
    """
    df = df.copy(deep=True)
    df['became_member_on'] = pd.to_datetime(df['became_member_on'], format="%Y%m%d")
    return df


def clean_transcript(df):
    """
    Initial cleaning of transcripts. Does not clean based on findings needing other input. See clean_dataset().
    :type df: pd.DataFrame
    """
    # Extract data from the value column
    df = df.copy(deep=True)
    df['value_keys'] = df['value'].apply(lambda d: list(d.keys()))

    offer_id = df.loc[:, ['value_keys', 'value']].apply(_value_return, axis=1,
                                                                wanted_key=['offer_id', 'offer id'])
    amount = df.loc[:, ['value_keys', 'value']].apply(_value_return, axis=1, wanted_key=['amount'])
    reward = df.loc[:, ['value_keys', 'value']].apply(_value_return, axis=1, wanted_key=['reward'])
    df['offer_id'] = offer_id
    df['amount'] = amount
    df['reward'] = reward
    #Remove unwanted columns
    df = df.drop(columns= ['value', 'value_keys'])
    df = df.rename(columns={'person': 'id'},)
    return df

def clean_data(portfolio, profile, transcript):
    """
    returns clean dataframes which has been cleaned based on cross data investigation from the exploratory analysis
    :param portfolio:
    :param profile:
    :param transcript:
    :return:
    """
    #perform initial cleaning
    portfolio_clean = clean_portfolio(portfolio)
    profile_clean = clean_profile_data(profile)
    transcript_clean = clean_transcript(transcript)

    #perform cleaning and imputes which are based on cross data undertanding

    #remove users with default profiles and no transactions
    non_informing_users = get_non_informing_users(transcript_clean, profile_clean)
    profile_clean = profile_clean[~profile_clean['id'].isin(non_informing_users)]
    transcript_clean = transcript_clean[~transcript_clean['id'].isin(non_informing_users)]

    return portfolio_clean, profile_clean, transcript_clean

def get_users_with_most_transactions(transcript,  n=2):
    """
    Return a list of user ids ranked from most transactions recorded
    :param transcript:
    :param n:
    :return:
    """
    idx = pd.IndexSlice
    grouped_person = transcript.groupby(by=['event','id']).count()
    ranked_person = grouped_person.loc[idx['transaction',:],:].sort_values(by='amount', ascending=False)
    ranked_person = ranked_person.reset_index(level=0, drop=True).reset_index()
    ranked_list = list(ranked_person['id'])
    if n>len(ranked_list):
        n = len(ranked_list)
    return ranked_list[:n]

def get_users_with_transactions(transcript):
    """
    Returns a list of user_ids for users that has performed any transactions
    :param transcript: a dataframe of transcripts
    :type transcript: pd.DataFrame
    :return:  list of userids
    """
    df = transcript.copy(deep=True)
    idx = pd.IndexSlice

    persons_with_transactions = df.loc[:, ['event', 'id', 'amount']].groupby(
        by=['event', 'id']).count()
    persons_with_transactions = persons_with_transactions.loc[idx['transaction', :], :].sort_values(
        'amount').reset_index(level=0, drop=True).reset_index()
    persons_with_transactions = persons_with_transactions['id']
    return list(persons_with_transactions)

def get_default_user(profile):
    """
    Return user ids with None gender, 118 age and nan income
    :param profile:
    :return: list of userids
    """
    df = profile.copy(deep=True)
    df = df.loc[df['gender'].isna(),:]
    return list(df['id'])

def get_non_informing_users(transcript, profile):
    """
    Returns user ids which are both default values and have no transactions in transcript
    :param transcript:
    :param profile:
    :return: list of user ids
    """
    default_users = get_default_user(profile)
    transaction_users = get_users_with_transactions(transcript)
    users_without_transactions = profile.loc[~profile['id'].isin(transaction_users),:]
    default_users_without_transactions = users_without_transactions.loc[users_without_transactions['id'].isin(default_users),'id']
    return list(default_users_without_transactions)




def _value_return(x, wanted_key = []):
    for key in x['value_keys']:
        if key in wanted_key:
            return x['value'][key]
    return np.nan


#transcript_clean.to_parquet("transcript_clean.parquet", compression='GZIP')