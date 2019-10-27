import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D


def simple_offer_plot(user, portfolio, profile, transcript, ax):
    """
    Return a figure with shaded boxes indicating the duration and reward value (height)
    :param users: list of user ids
    :param portfolio: cleaned portfolio dataframe
    :param profile: cleaned profile dataframe
    :param transcript: cleaned transcript dataframe
    :return: ax object
    """

    user_transcript = transcript.loc[transcript['id'] == user, :]
    # get all offer data
    offers_start = np.array(user_transcript.loc[user_transcript['event'] == 'offer received', 'time'])
    offer_duration = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'duration'].values.astype(int)[0] * 24 for offer_id in
         user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id']])
    offer_reward = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'reward'].values.astype(int)[0] * 2 + 1 for offer_id in
         user_transcript.loc[user_transcript[
                                  'event'] == 'offer received', 'offer_id']])  # times 2 and +1 to avoid having boxes with 0 height

    offers_end = np.array(user_transcript.loc[user_transcript['event'] == 'offer received', 'time']) + offer_duration
    offers_viewed = np.array(user_transcript.loc[user_transcript['event'] == 'offer viewed', 'time'])

    print(user, list(zip(offers_start, offers_end)), np.array(offer_duration), np.array(offer_reward))

    # make shaded boxes
    offerboxes = []
    plt.vlines(offers_start, -30, 30, 'g')
    plt.vlines(offers_end, -30, 30, 'r')
    offerboxes = []
    for (start, duration), height in zip(zip(offers_start, offer_duration), offer_reward):
        rec_offers = Rectangle((start, -height / 2), duration, height)
        offerboxes.append(rec_offers)
    pc_offers = PatchCollection(offerboxes, alpha=0.3, edgecolor='k', facecolor='g', linewidth=4)
    ax.add_collection(pc_offers)
    ax.set_xlabel('Time [h]')
    ax.set_ylabel('USD')
    return ax

def detailed_offer_plot(user, portfolio, profile, transcript):
    # get user related data
    user_transcript = transcript.loc[transcript['id'] == user, :]
    user_profile = profile.loc[profile['id'] == user, :]
    user_transactions = user_transcript.loc[user_transcript['event'] == 'transaction', ['time', 'amount']]

    # plot params
    max_transaction = user_transactions['amount'].max()
    mheight = max_transaction
    mcntr = mheight / 2
    mrksize = 15

    # get offer history
    offer_ids = [(i, offer_id) for i, offer_id in
                 enumerate(user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id'])]
    offers_start = np.array(user_transcript.loc[user_transcript['event'] == 'offer received', 'time'])
    offers_type = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'offer_type'].values.astype(str)[0] for offer_id in
         user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id']])
    offers_difficulty = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'difficulty'].values.astype(str)[0] for offer_id in
         user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id']])
    offers_reward = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'reward'].values.astype(str)[0] for offer_id in
         user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id']])
    n_offers = len(offers_start)
    offers_duration = np.array(
        [portfolio.loc[portfolio['id'] == offer_id, 'duration'].values.astype(int)[0] * 24 for offer_id in
         user_transcript.loc[user_transcript['event'] == 'offer received', 'offer_id']])
    offers_end = np.array(user_transcript.loc[user_transcript['event'] == 'offer received', 'time']) + offers_duration
    offers_viewed = np.array(user_transcript.loc[user_transcript['event'] == 'offer viewed', ['time', 'offer_id']])
    offers_completed = np.array(
        user_transcript.loc[user_transcript['event'] == 'offer completed', ['time', 'offer_id']])

    fig, axs = plt.subplots(n_offers + 1, 1, sharex=True, figsize=(12, 1 * n_offers));
    for i, ax in enumerate(axs[:-1]):
        offer_id = offer_ids[i][1]
        offer_start = offers_start[i]
        offer_end = offers_end[i]
        offer_duration = offers_duration[i]
        offer_type = offers_type[i]
        offer_difficulty = offers_difficulty[i]
        offer_reward = offers_reward[i]
        offer_completed = None
        offer_viewed = None

        # Check if any completion for offer id is within duration
        for time, completion_offer_id in offers_completed:
            if completion_offer_id == offer_id and time >= offer_start and time <= offer_end:
                offer_completed = time
                break

                # Check if any offer viewed for offer id is within duration
        for time, viewed_offer_id in offers_viewed:
            if viewed_offer_id == offer_id and time >= offer_start and time <= offer_end:
                offer_viewed = time
                break

                # print(offer_id, offer_start, offer_end, offer_duration, offer_completed, offer_type)

        offer_rec = Rectangle((offer_start, 0), offer_duration, mheight, facecolor='silver', alpha=0.5, edgecolor='k',
                              linewidth=2)
        ax.add_patch(offer_rec)

        ax.plot(offer_start, mcntr, 'g', marker=5, markersize=mrksize, label='offer start')
        ax.plot(offer_end, mcntr, 'r', marker=4, markersize=mrksize, label='offer end')
        if offer_viewed and offer_completed:
            if offer_viewed <= offer_completed:
                ax.plot(offer_viewed, mcntr, 'y', marker='d', markersize=mrksize, label='viewed offer')
                ax.plot(offer_completed, mcntr, 'b', marker='*', markersize=mrksize, label='completed offer')
            else:
                ax.plot(offer_viewed, mcntr, 'maroon', marker='d', markersize=mrksize, label='viewed after completion')
                ax.plot(offer_completed, mcntr, 'b', marker='*', markersize=mrksize, label='completed offer')
        elif offer_viewed:
            ax.plot(offer_viewed, mcntr, 'y', marker='d', markersize=mrksize, label='viewed offer')
        if offer_completed:
            ax.plot(offer_completed, mcntr, 'b', marker='*', markersize=mrksize, label='completed offer')
        text_x = 600
        if offer_start > 150:
            text_x = 2
        elif offer_start < 550:
            text_x = 600

        # plot transactions
        transactions_offer = user_transactions.loc[(user_transactions['time'] >= offer_start) &
                                                   (user_transactions['time'] <= offer_end), :]
        transactions_not_offer = user_transactions.loc[(user_transactions['time'] < offer_start) &
                                                       (user_transactions['time'] > offer_end), :]

        for row in transactions_offer.iterrows():
            ax.vlines(row[1]['time'], 0, row[1]['amount'], 'k', linewidth=3, label='transaction amount')
        ax.text(text_x, 2,
                s="offer type: {}\ndifficulty: {}\nreward: {}".format(offer_type, offer_difficulty, offer_reward),
                fontdict=dict(size=10))
        ax.set_xlim((-20, 750))
        ax.set_ylim((-mheight * .05, mheight * 1.05))
        ax.grid(False)

    legend_elements = [Line2D([0], [0], color='g', marker=5, linewidth=0, markersize=mrksize, label='offer start'),
                       Line2D([0], [0], color='r', marker=4, linewidth=0, markersize=mrksize, label='offer end'),
                       Line2D([0], [0], color='y', marker='d', linewidth=0, markersize=mrksize, label='viewed offer'),
                       Line2D([0], [0], color='b', marker='*', linewidth=0, markersize=mrksize,
                              label='completed offer'),
                       Line2D([0], [0], color='maroon', marker='d', linewidth=0, markersize=mrksize,
                              label='viewed after completion'),
                       Line2D([0], [0], color='k', marker='|', linewidth=0, markersize=mrksize,
                              label='transaction [USD]'),
                       Line2D([0], [0], color='b', linewidth=1, label='cumulative spending [USD]')]
    fig.subplots_adjust(top=0.9, right=0.9, hspace=0.05)
    plt.legend(handles=legend_elements, mode='expand', fontsize=8, ncol=len(legend_elements), loc='lower left',
               bbox_to_anchor=(0.1, 0.9, 0.81, 0.9), bbox_transform=plt.gcf().transFigure)

    # plot accumulated amount
    user_transactions['cumsum'] = user_transactions['amount'].cumsum()
    df1 = user_transactions
    df2 = user_transactions.copy(deep=True).iloc[:-1, :]
    shifted_time = np.array(df1.loc[:, 'time'].iloc[1:, ])
    df2.loc[:, 'time'] = shifted_time
    interleaved_transactions = pd.concat((df1, df2)).reset_index().sort_values(['time', 'index'])
    axs[-1].plot(interleaved_transactions['time'], interleaved_transactions['cumsum'], 'b', label='cumulative spending')
    axs[-1].grid(True)
    return fig



