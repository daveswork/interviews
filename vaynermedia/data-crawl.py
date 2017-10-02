'''
Tested and executed on Python 3.6

'''



import pandas as pd
import json
import numpy as np
import time

#Added for timing task.
start_time = time.time()

#These are going in the global namespace as they get used frequently enough.
source1_df = pd.read_csv("source1.csv")
source2_df = pd.read_csv("source2.csv")
campaigns_in_source2 = source2_df.campaign_id.unique()


def get_spend_for_campaign(campaign):
    '''
    Checks to see if a campaign exists in the source2 dataframe.
    If it's there, lets return a total of the spend.
    If not, return 0 as the spend.
    '''
    total_spent = 0
    if campaign in campaigns_in_source2:
        total_spent = source2_df[source2_df["campaign_id"] == campaign].spend.sum()
    return total_spent


def get_action_totals(df,agg_by_sum=True):
    '''
    Returns a pivot table using actions as the index given a data frame.
    This would have to be from Source 2, or some subset of Source 2 data.
    '''
    actions = df['actions'].tolist()
    action_list = []
    for item in actions:
        act = json.loads(item)
        action_list.extend(act)
    action_df = pd.DataFrame.from_records(action_list)
    if agg_by_sum:
        return pd.pivot_table(action_df, index="action", aggfunc=np.sum)
    else:
        return pd.pivot_table(action_df, index="action", aggfunc="count")


def tally_cost(df, list):
    '''
    Returns the total spent on a list of campaigns.
    '''
    total = 0
    for item in list:
        total += get_spend_for_campaign(item)
    return total


def campaigns_by_haircolor(df, color):
    '''
    Returns a list of unique campaign ids for given hair color.
    '''
    color_df = df[df["audience"].str.contains(color)].campaign_id.unique()
    return color_df


def campaigns_by_number_of_days(df, duration):
    '''
    Returns a list of campaigns that have run for longer than the specified duration.
    '''
    #Generate a list of unique campaign ids.
    campaign_list = df.campaign_id.unique()
    #This list will hold campaign ids for those campaigns of interest to us.
    target_list = []
    #For each campaign get a list of days that it we have reported data for.
    #Then count how many days and compare it.
    for campaign in campaign_list:
        campaign_frequency = df[df["campaign_id"] == campaign]
        if len(campaign_frequency.date.unique()) >= duration:
            target_list.append(campaign)
    return target_list


def get_source_action_type(df, source, action_type):
    '''
    Returns the number of times a source reported on a specified action type.
    '''
    action_list = (df['actions'].tolist())
    test_list = []
    for item in action_list:
        test = json.loads(item)
        test_list.extend(test)
    test_df = pd.DataFrame.from_records(test_list)
    return test_df[test_df['action']==action_type][source].count()


def get_more_junk_than_noise(df):
    '''
    Returns a list of sources which report more junk than noise.
    This works by getting a count of different actions by source.
    Then comparing the junk vs noise totals for each source.
    '''
    total_df = get_action_totals(df)
    sources = total_df.columns.values
    interesting_sources = []
    for source in sources:
        if total_df.loc["junk", source] > total_df.loc["noise", source]:
            interesting_sources.append(source)
    return interesting_sources


def get_spend_on_ad_type(df, type):
    '''
    Returns the total spent on a particular type of ad per view.
    First get the total spent, then the number of reported views.
    Per ad spend is calculated by diving the amount spent by total views.
    '''
    df_type = df[df.ad_type == type]
    total_spent = df_type.spend.sum()
    total_actions = get_action_totals(df_type)
    total_views = total_actions.loc['views'].sum()
    return round(total_spent/total_views, 2)


def conversion_for_state_for_source(df, state, source):
    '''
    Returns the number of conversions per state as reported by a particular source.
    '''
    total = 0
    state_campaigns = df[df["audience"].str.contains(state)].campaign_id.unique()
    campaigns_with_data = source2_df.campaign_id.unique()
    for campaign in state_campaigns:
        if campaign in campaigns_with_data:
            campaign_df = source2_df[source2_df["campaign_id"]==campaign]
            action_summary = get_action_totals(campaign_df)
            if source in action_summary.columns.values:
                if "conversions" in action_summary.index.values:
                    if action_summary.loc["conversions", source] > 0:
                        total += action_summary.loc["conversions", source]
    return total


def best_cpm_of_state_hair_color_combo():
    '''
    This one is a bit tricky.
    The approach here is to get the total impressions per campain.
    Then the total spent for each campaign.
    With those values we can than calculate the CPM after we've arranged our data.
    Alternatively, a simpler method would've been to calculate the CPM, then just
    return the state/hair-color value for that campain. Hrmm, need some feedback..
    '''
    #First let's break out the state and hair color values into their own columns
    source1_df['state'] = source1_df.audience.apply(lambda x: x.split("_")[0])
    source1_df['hair_color'] = source1_df.audience.apply(lambda x: x.split("_")[1])
    #Now, let's break out the campain, state and hair color into their own df, this should sum the impressions.
    unique_campaigns_df = source1_df.groupby(['campaign_id', 'state', 'hair_color']).sum().reset_index()
    #Let's the get the spend on each campaign.
    unique_campaigns_df['spend'] = unique_campaigns_df.campaign_id.apply(lambda x: get_spend_for_campaign(x))
    #Now breaking out the state & hair color into their own df, that should sum the impressions and spend.
    unique_campaigns_df['state_hair'] = unique_campaigns_df['state'] + '_' + unique_campaigns_df['hair_color']
    state_with_hair_color_df = unique_campaigns_df.groupby('state_hair').sum().reset_index()
    #Calculate the CPM for each unique state/hair color combo and return the best one.
    state_with_hair_color_df['cpm'] = (state_with_hair_color_df.impressions / state_with_hair_color_df.spend) * 1000
    return state_with_hair_color_df.loc[state_with_hair_color_df.cpm.idxmax(), 'state_hair']


campaigns = campaigns_by_haircolor(source1_df, "purple")
#Task 1, spend on campaigns run against people with purple hair.
task1_ans = "Task 1: " + str(tally_cost(source2_df, campaigns)) + "\n"
#Task 2, number of campaigns that ran for longer than 4 days.
task2_ans = "Task 2: " + str(len(campaigns_by_number_of_days(source2_df, 4))) + "\n"
#Task 3, number of times source H reported on clicks.
task3_ans = "Task 3: " + str(get_source_action_type(source2_df,"H", "clicks" )) + "\n"
#Task 4, a list of sources that reported more junk than noise.
task4_ans = "Task 4: " + str(get_more_junk_than_noise(source2_df)) + "\n"
#Task 5, cost per view of all video ads.
task5_ans = "Task 5: " + str(get_spend_on_ad_type(source2_df, "video")) + "\n"
#Task 6, number of conversions reported by source H for NY
task6_ans = "Task 6: " + str(conversion_for_state_for_source(source1_df, "NY", "H")) + "\n"
#Task 7, best CPM grouped by state & hair color combo.
task7_ans = "Task 7: " + str(best_cpm_of_state_hair_color_combo()) + "\n"

execution_time = "Execution time: "+ str(time.time() - start_time) + "\n"
with open('answers.txt', 'w+') as answers:
    answers.write(task1_ans)
    answers.write(task2_ans)
    answers.write(task3_ans)
    answers.write(task4_ans)
    answers.write(task5_ans)
    answers.write(task6_ans)
    answers.write(task7_ans)
    answers.write(execution_time)
