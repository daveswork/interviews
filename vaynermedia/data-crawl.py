import pandas as pd
import json
import numpy as np

source1_df = pd.read_csv("source1.csv")
source2_df = pd.read_csv("source2.csv")

def campaigns_by_haircolor(df, color):
    '''
    Returns a list of unique campaign ids for given hair color.
    '''
    color_df = df[df["audience"].str.contains(color)].campaign_id.unique()
    return color_df

def tally_cost(df, list):
    '''
    Returns the total spent on a list of campaigns.
    '''
    total = 0
    #Need to verify that each item in the list is also in the referenced df
    for item in list:
        total += df[df["campaign_id"]==item].spend.sum()
    return total

#campaigns = campaigns_by_haircolor(source1_df, "purple")

#print(tally_cost(source2_df, campaigns))

#print(source2_df.campaign_id.unique())

def campaigns_by_number_of_days(df, duration):
    '''
    Returns a list of campaigns that have run for longer than the specified duration.
    '''
    #Generate a list of unique campaign ids.
    campaign_list = df.campaign_id.unique()
    #This list will hold campaign ids for those campaigns of interest to us.
    target_list = []
    for campaign in campaign_list:
        campaign_frequency = df[df["campaign_id"] == campaign]
        if len(campaign_frequency.date.unique()) >= duration:
            #if campaign_frequency.spend.sum() > 0:
            target_list.append(campaign)
            #test = json.loads(campaign_frequency['actions'].tolist()[0])
            #test_df = pd.DataFrame.from_records(test)
            #print(test[0])
            #for item in test:
                #test_df.append(item, ignore_index=True)
                #print(item)
            #print(test_df)
    return target_list

#print(len(campaigns_by_number_of_days(source2_df, 4)))

def get_source_action_type(df, source, action_type):
    '''
    Returns the number of times a source reported on a specified action type.
    '''
    action_list = (df['actions'].tolist())
    #test_df = pd.DataFrame.from_records(test)
    test_list = []
    for item in action_list:
        test = json.loads(item)
        test_list.extend(test)
    #print(test_list[-1])
    test_df = pd.DataFrame.from_records(test_list)
    return test_df[test_df['action']==action_type][source].count()
    #print(test_df.pivot(index=["A"],columns="action"))
    #print(pd.pivot_table(test_df, index="action", aggfunc='count'))
    #print(pd.pivot_table(test_df, index="action", aggfunc=np.sum))
    #print(test_df.columns.values)

#print(get_source_action_type(source2_df,"H", "clicks" ))



def get_more_junk_than_noise(df):
    '''
    Returns a list of sources which report more junk than noise.
    '''
    action_list = (df['actions'].tolist())
    #test_df = pd.DataFrame.from_records(test)
    test_list = []
    for item in action_list:
        test = json.loads(item)
        test_list.extend(test)
    #print(test_list[-1])
    test_df = pd.DataFrame.from_records(test_list)
    #print(test_df[test_df['action']=='clicks'][source].count())
    #print(test_df.pivot(index=["A"],columns="action"))
    reported_df = pd.pivot_table(test_df, index="action", aggfunc='count')
    total_df = pd.pivot_table(test_df, index="action", aggfunc=np.sum)
    sources = reported_df.columns.values
    #print(reported_df.loc["clicks","A"])
    interesting_sources = []
    for source in sources:
        if total_df.loc["junk", source] > total_df.loc["noise", source]:
            interesting_sources.append(source)
    return interesting_sources

#print(get_more_junk_than_noise(source2_df))

def get_spend_on_ad_type(df, type):
    df_type = df[df.ad_type == type]
    total_spent = df_type.spend.sum()
    actions = df_type['actions'].tolist()
    action_list = []
    for item in actions:
        act = json.loads(item)
        action_list.extend(act)
    action_df = pd.DataFrame.from_records(action_list)
    total_actions = pd.pivot_table(action_df, index="action", aggfunc=np.sum)
    total_views = total_actions.loc['views'].sum()
    return round(total_spent/total_views, 2)

#print(get_spend_on_ad_type(source2_df, "video"))

def get_action_totals(df):
    '''
    Returns a pivot table with a count of actions given a data frame.
    '''
    actions = df['actions'].tolist()
    action_list = []
    for item in actions:
        act = json.loads(item)
        action_list.extend(act)
    action_df = pd.DataFrame.from_records(action_list)
    return pd.pivot_table(action_df, index="action", aggfunc=np.sum)



def conversion_for_state_for_source(df, state, source):
    total = 0
    state_campaigns = df[df["audience"].str.contains(state)].campaign_id.unique()
    #print(state_campaigns)
    #print(source2_df[source2_df["campaign_id"]==state_campaigns[0]])
    #print(get_action_totals(source2_df[source2_df["campaign_id"]==state_campaigns[4]]))
    #print(source2_df[source2_df["campaign_id"]==state_campaigns[4]])
    #print(state_campaigns[4])
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




#print(conversion_for_state_for_source(source1_df, "NY", "A"))
#print(len(source1_df.audience.unique()))


campaigns_in_source2 = source2_df.campaign_id.unique()

def get_spend_for_campaign(campaign):
    total_spent = 0
    if campaign in campaigns_in_source2:
        total_spent = source2_df[source2_df["campaign_id"] == campaign].spend.sum()
    return total_spent


def best_cpm_of_state_hair_color_combo():

    source1_df['state'] = source1_df.audience.apply(lambda x: x.split("_")[0])
    source1_df['hair_color'] = source1_df.audience.apply(lambda x: x.split("_")[1])
    #print(pd.pivot_table(source1_df, index=["state"], columns=["hair_color"], values="impressions", aggfunc=np.sum, margins=True))

    '''
    Sort on duplicated campaign_id
    '''
    #camp_ids = source1_df["campaign_id"]
    #source1_df[source1_df.duplicated(['campaign_id'], keep=False)].to_csv("test.csv")


    unique_campaigns_df = source1_df.groupby(['campaign_id', 'state', 'hair_color']).sum().reset_index()
    #print(unique_campaigns_df)

    unique_campaigns_df['spend'] = unique_campaigns_df.campaign_id.apply(lambda x: get_spend_for_campaign(x))

    unique_campaigns_df['state_hair'] = unique_campaigns_df['state'] + '_' + unique_campaigns_df['hair_color']

    state_with_hair_color_df = unique_campaigns_df.groupby('state_hair').sum().reset_index()

    state_with_hair_color_df['cpm'] = (state_with_hair_color_df.impressions / state_with_hair_color_df.spend) * 1000

    print(state_with_hair_color_df.loc[state_with_hair_color_df.cpm.idxmin(), 'state_hair'])
    #state_with_hair_color_df.to_csv('state_hair.csv')
