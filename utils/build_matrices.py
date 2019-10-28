import numpy as np
import pandas as pd


def build_user_df(portfolio, profile, transcript, offers):
    users = np.array(profile['id'])

    user_dict = {}
    max_time = transcript.loc[:, 'time'].max()

    for user in users:
        user_transcript = transcript.loc[transcript['id'] == user, :]

        user_transactions = user_transcript.loc[user_transcript['event'] == 'transaction', ['time', 'amount']]
        user_offers = offers[offers['user_id'] == user]

        total_spent = user_transactions['amount'].sum()
        # It would be tempting to do: total_spent_in_window = user_offers['amount_in_window'].sum()
        # that is not possible since we have overlapping offers, that counts the spending twice.
        # Instead we have to mask any transaction in the union of time windows
        spent_in_window = 0
        spent_in_discount_window = 0
        spent_in_bogo_window = 0
        spent_in_info_window = 0
        spent_no_window = 0
        for i, row in user_transactions.iterrows():
            # the below test is based on the fact that comparing a value with nan returns false, thus if not viewed, automatically it will be nan
            # the test checks if the transaction time is inside any of the "valid windows" of all offers given to the user.
            transaction_in_window = np.any((user_offers['view_time'] <= row['time']) &
                                           (user_offers['view_time'] + user_offers['time_in_window'] >= row['time']))
            if transaction_in_window:
                spent_in_window += row['amount']
            else:
                spent_no_window += row['amount']

        assert np.isclose(spent_in_window + spent_no_window, total_spent, rtol=1e-5,
                          atol=1e-3), 'summation of spendings not correct'

        # Get amount spent in specific windows. Here, double booking is allowed to happen
        spent_in_discount_window = user_offers.loc[user_offers['offer_type'] == 'discount', 'amount_in_window'].sum()
        spent_in_bogo_window = user_offers.loc[user_offers['offer_type'] == 'bogo', 'amount_in_window'].sum()
        spent_in_info_window = user_offers.loc[user_offers['offer_type'] == 'informational', 'amount_in_window'].sum()

        # Get time spent in any window
        windows = list(zip(user_offers['view_time'], user_offers['view_time'] + user_offers['time_in_window']))
        intervals = merged_intervals(windows)
        time_in_windows = np.diff(np.array(intervals).transpose(), axis=0).sum()
        time_no_windows = max_time - time_in_windows

        windows_discount = list(zip(user_offers.loc[user_offers['offer_type'] == 'discount', 'view_time'],
                                    user_offers.loc[user_offers['offer_type'] == 'discount', 'view_time'] +
                                    user_offers.loc[user_offers['offer_type'] == 'discount', 'time_in_window']))
        intervals_discount = merged_intervals(windows_discount)
        windows_bogo = list(zip(user_offers.loc[user_offers['offer_type'] == 'bogo', 'view_time'],
                                user_offers.loc[user_offers['offer_type'] == 'bogo', 'view_time'] +
                                user_offers.loc[user_offers['offer_type'] == 'bogo', 'time_in_window']))
        intervals_bogo = merged_intervals(windows_bogo)
        windows_info = list(zip(user_offers.loc[user_offers['offer_type'] == 'informational', 'view_time'],
                                user_offers.loc[user_offers['offer_type'] == 'informational', 'view_time'] +
                                user_offers.loc[user_offers['offer_type'] == 'informational', 'time_in_window']))
        intervals_info = merged_intervals(windows_info)
        time_in_discount = np.diff(np.array(intervals_discount).transpose(), axis=0).sum()
        if np.isnan(time_in_discount):
            time_in_discount = 0
        time_in_bogo = np.diff(np.array(intervals_bogo).transpose(), axis=0).sum()
        if np.isnan(time_in_bogo):
            time_in_bogo = 0
        time_in_info = np.diff(np.array(intervals_info).transpose(), axis=0).sum()
        if np.isnan(time_in_info):
            time_in_info = 0

        if user_offers.shape[0] == 0:
            print("user {} has no offers to extract data from".format(user))
            view_ratio = 0
            completion_ratio = 0
            view_and_complete_ratio = 0
        else:
            view_ratio = user_offers['viewed'].sum() / user_offers.shape[0]
            completion_ratio = user_offers['completed'].sum() / user_offers.shape[0]
            view_and_complete_ratio = user_offers.loc[(user_offers['completed'] == 1) & (
                        user_offers['viewed'] == 1), 'start_time'].count() / user_offers.shape[0]

        user_dict.update({user: {'spent_total': total_spent,
                                 'spent_in_window': spent_in_window,
                                 'spent_no_window': spent_no_window,
                                 'spent_in_discount': spent_in_discount_window,
                                 'spent_in_bogo': spent_in_bogo_window,
                                 'spent_in_informational': spent_in_info_window,
                                 'time_in_window': float(time_in_windows) + 1,
                                 # add one to avoid infinity for users that view, spend and complete in the same hour
                                 'time_no_window': time_no_windows + 1,
                                 'time_in_discount': time_in_discount + 1,
                                 'time_in_bogo': time_in_bogo + 1,
                                 'time_in_informational': time_in_info + 1,
                                 'view_ratio': view_ratio,
                                 'completion_ratio': completion_ratio,
                                 'view_and_complete_ratio': view_and_complete_ratio,
                                 'num_offers_received': user_offers.shape[0]}})

    expanded = pd.DataFrame.from_dict(user_dict, orient='index').reset_index().rename(columns={'index': 'user_id'})

    profile_expanded = pd.merge(profile.sort_values('id'), expanded.sort_values('user_id'), left_on='id',
                                right_on='user_id').drop(columns='id')
    return profile_expanded


def build_offer_df(portfolio, profile, transcript):
    # iterate over users
    users = profile['id'].unique()

    offers = {}
    count = 0
    count_users_no_offer = 0
    for user in users:
        # transcripts for specific user
        user_transcript = transcript.loc[transcript['id'] == user, :]
        user_transactions = user_transcript.loc[user_transcript['event'] == 'transaction', ['time', 'amount']]
        offer_ids_tuples = get_user_offer_ids(user_transcript)
        if len(offer_ids_tuples) < 1:  # if there are no offers given to user, skip the rest.
            count_users_no_offer += 1
            continue
        offer_ids = list(list(zip(*offer_ids_tuples))[1])

        offers_start = get_user_offer_starts(user_transcript)
        offers_duration = get_user_offer_durations(portfolio, offer_ids)
        offers_difficulty = get_user_offer_difficulties(portfolio, offer_ids)
        offers_reward = get_user_offer_rewards(portfolio, offer_ids)
        offers_type = get_user_offer_types(portfolio, offer_ids)
        offers_viewed = get_user_offer_views(user_transcript)
        offers_completed = get_user_offer_completions(user_transcript)

        offers_end = offers_start + offers_duration

        # Test if results are as expected
        assert len(offer_ids) == len(
            offers_start), "The number of offerings ({}) are not the same as the number of starting points ({})".format(
            len(offer_ids), len(offers_start))
        assert len(offer_ids) == len(
            offers_type), "The number of offerings ({}) are not the same as the number of offer types ({})".format(
            len(offer_ids), len(offers_type))
        assert len(offer_ids) == len(
            offers_difficulty), "The number of offerings ({}) are not the same as the number of offer difficulties ({})".format(
            len(offer_ids), len(offers_difficulty))
        assert len(offer_ids) == len(
            offers_reward), "The number of offerings ({}) are not the same as the number of offer rewards ({})".format(
            len(offer_ids), len(offers_reward))
        assert len(offer_ids) == len(
            offers_duration), "The number of offerings ({}) are not the same as the number of offer durations ({})".format(
            len(offer_ids), len(offers_duration))

        # iterate over offers and build dict to be used to fill a dataframe
        for i, offer_id in offer_ids_tuples:
            start = offers_start[i]
            duration = offers_duration[i]
            end = offers_end[i]
            kind = offers_type[i]
            reward = offers_reward[i]
            difficulty = offers_difficulty[i]

            # identify completion event within the offer
            completed_time = None
            completed = 0  # 0 if no completion even, 1 if completion even
            for time, completion_offer_id in offers_completed:
                if completion_offer_id == offer_id and time >= start and time <= end:
                    completed_time = time
                    completed = 1
                    break

            # identify view event within the offer, views after completion will be regarded as not viewed
            viewed_time = None
            viewed = 0  # 0 if no completion even, 1 if completion even
            for time, viewed_offer_id in offers_viewed:
                if completed_time:
                    if time > completed_time:  # do not accept if time of viewing is after time of completion
                        break
                if viewed_offer_id == offer_id and time >= start and time <= end:
                    viewed_time = time
                    viewed = 1
                    break

                    # calculate valid window related parameters
            time_in_window = 0
            amount_in_window = 0
            if viewed:
                # time from viewed to completion or end of offer window.
                if completed_time:
                    time_in_window = completed_time - viewed_time + 1
                else:
                    time_in_window = end - viewed_time + 1
                    # cumulative amount spent in valid window, if no valid window, no amount spent due to offer
                transactions_in_window = user_transactions.loc[(user_transactions['time'] >= viewed_time) &
                                                               (user_transactions[
                                                                    'time'] <= viewed_time + time_in_window), :]

                amount_in_window = transactions_in_window['amount'].sum()

            offers.update({count: {'offer_id': offer_id,
                                   'user_id': user,
                                   'offer_type': kind,
                                   'difficulty': difficulty,
                                   'reward': reward,
                                   'start_time': start,
                                   'duration': duration,
                                   'end_time': end,
                                   'viewed': viewed,
                                   'view_time': viewed_time,
                                   'completed': completed,
                                   'complet_time': completed_time,
                                   'time_in_window': time_in_window,
                                   'amount_in_window': amount_in_window}})
            count += 1
    offer_df = pd.DataFrame.from_dict(offers, orient='index')
    offer_type_dummies = pd.get_dummies(offer_df.loc[:, 'offer_type'], prefix='type')
    offer_df = offer_df.merge(offer_type_dummies, left_index=True, right_index=True)
    print("{} received no offer".format(count_users_no_offer))
    return offer_df


def get_user_offer_ids(user_transcript):
    """
    Extracts offer ids presented to the user
    """
    offer_ids = [(i, offer_id) for i, offer_id in
                 enumerate(user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id'])]
    return offer_ids


def get_user_offer_starts(user_transcript):
    """
    Extracts start times of offers presented to the user
    """
    offers_start = np.array(user_transcript.loc[user_transcript['event'] == 'offer received', 'time'])
    return offers_start


def get_user_offer_types(portfolio, offer_ids):
    """
    Extracts offer types of offers presented to the user
    """
    offers_type = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'offer_type'].values.astype(str)[0] for offer_id in offer_ids])
    return offers_type


def get_user_offer_difficulties(portfolio, offer_ids):
    """
    Extracts difficulty of offers presented to the user
    """
    offers_difficulty = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'difficulty'].values.astype(str)[0] for offer_id in offer_ids])
    return offers_difficulty


def get_user_offer_rewards(portfolio, offer_ids):
    """
    Extracts difficulty of offers presented to the user
    """
    offers_reward = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'reward'].values.astype(str)[0] for offer_id in offer_ids])
    return offers_reward


def get_user_offer_durations(portfolio, offer_ids):
    """
    Extracts difficulty of offers presented to the user
    """
    offers_duration = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'duration'].values.astype(int)[0] * 24 for offer_id in offer_ids])
    return offers_duration


def get_user_offer_views(user_transcript):
    """
    Extracts difficulty of offers presented to the user
    """
    offers_viewed = np.array(user_transcript.loc[user_transcript['event'] == 'offer viewed', ['time', 'offer_id']])
    return offers_viewed


def get_user_offer_completions(user_transcript):
    """
    Extracts difficulty of offers presented to the user
    """
    offers_completed = np.array(
        user_transcript.loc[user_transcript['event'] == 'offer completed', ['time', 'offer_id']])
    return offers_completed


def merged_intervals(windows):
    """
    Returns a list of list with merged intervals. Assume sort start times.
    Expect a list of list of the form [[starttime, endtime], [starttime, endtime],...]
    Sorts by start time and returns a list of list ordered
    """
    if len(windows) == 0:
        return [[0], [0]]
    if np.all([np.isnan(s) for s, e in windows]):
        return [[0], [0]]
    windows.sort(key=lambda x: x[0])
    while np.isnan(windows[0][0]):
        windows.pop(0)
    intervals = [[windows[0][0], windows[0][1]]]
    if len(windows) == 1:
        return intervals
    for start, end in windows[1:]:
        if np.isnan(start) or np.isnan(end):
            continue
        if start < intervals[-1][1]:
            if end > intervals[-1][
                1]:  # if start of next window is less than current interval, then change interval end
                intervals[-1][1] = end
        else:
            intervals.append([start, end])
    return intervals


