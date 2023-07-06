from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================
# split data stored as a string into a key and value
# data is usually structured data-key but is sometimes structured key-data
# the left input is used to determine which structure should be applied
# output is an updated player dictionary
def split_data(full_text, search_text, left, add_dictionary):
    if full_text.find(search_text) >= 0:
        key_value = search_text
        if left:
            data_value = full_text[0:full_text.find(search_text)]
        else:
            data_value = full_text[(full_text.find(search_text) + len(search_text)):]
        add_dictionary.update({key_value: data_value})
        return add_dictionary
    return add_dictionary


# ======================================================================================================================
# DEFAULT VALUES
# ======================================================================================================================
# identify which keys we want to drop from the player stats dictionary
dict_drop = ['optaId', 'fullName', 'knownName', 'clubOptaId', 'thumbnail', 'playerStatusList', 'playerSlug']

# create the initial dataframe (empty) so we can concatenate dataframes built off of player dictionaries
all_data = pd.DataFrame()

# build list of club tags and iterate over that list to capture all clubs
club_list = ('atl', 'atx', 'clt', 'chi', 'cin', 'col', 'clb', 'dal', 'dc', 'hou', 'skc', 'la', 'lafc', 'mia', 'min',
             'mtl', 'nsh', 'ne', 'rbny', 'nyc', 'orl', 'phi', 'por', 'rsl', 'sj', 'sea', 'stl', 'tor', 'van')
# NOTE: the nyc roster button href is incorrect, it should be '/clubs/new-york-city-football-club/roster/'
#       the stl roster button is also incorrect, it should just be '/clubs/st-louis-city-sc/roster/'

# build lists to clarify the different success rate data values
success_list = ['Tackles', 'Duels', 'Aerial Duels', 'Passes', 'Long Passes']
success_list_gk = ['Saves', 'Passes', 'Long Passes']

# build a list of the main data tags we are going to look for, these are structured value-key
data_list = ('Games played', 'Minutes played', 'Starts', 'Subbed off', 'Clearances', 'Blocks', 'Interceptions',
             'Total passes', 'Successful passes', 'Passes per 90 mins', 'Total open play crosses', 'Succ. crosses',
             'Assists', 'Second assists', 'Key Passes', 'Conversion rate', 'Mins per goal', 'Left foot goals',
             'Right foot goals', 'Headed goals', 'Other', 'Goals inside the box', 'Goals outside the box',
             'Direct free kick goals', 'Fouls won', 'Fouls conceded', 'Yellow cards', 'Red cards', 'Clean sheets',
             'Catches', 'Punches', 'Drops', 'Penalties saved', 'Clearances')

# build a list of the data tags we want that are backwards (key-value rather than value-key)
data_list_flip = ('Total shots (excluding blocked shots)', 'Shots on target', 'Goals scored')

# ======================================================================================================================
# MAIN LOOP
# ======================================================================================================================
# load start page (list of all clubs with buttons to see their rosters or stats)
base_url = "https://www.mlssoccer.com"
team_url = base_url + "/players/"
page = requests.get(team_url)
soup = bs(page.content, "html.parser")

# loop over all of the clubs
for target_club in club_list:
    print(target_club)
    print('---------------------------------------------')
    # pull a specific team's portion of the html, then isolate its roster button and corresponding url
    team = soup.find("div", class_=f"club-card {target_club}")
    roster_button = team.find("li", class_="button1")
    roster_link = roster_button.find("a").get('href')

    # NYC's roster button link is currently incorrect, this is the correct link
    if target_club == 'nyc':
        roster_link = '/clubs/new-york-city-football-club/roster/'

    # STL's roster button includes the full link rather than the add-on to the base url
    if target_club == 'stl':
        roster_link = '/clubs/st-louis-city-sc/roster/'

    # go to the new url for the specific team's roster, waiting to avoid overload
    sleep(5)
    roster_url = base_url + roster_link
    roster_page = requests.get(roster_url)
    roster_soup = bs(roster_page.content, "html.parser")

    # on that roster, pull a list of players
    player_data = roster_soup.find("section", class_="mls-l-module mls-l-module--active-roster")
    table_data = player_data['data-options']
    overall_dictionary = json.loads(table_data)
    player_dictionary = overall_dictionary['playersData']

    # loop over all players on the team
    for player in player_dictionary:
        print(player.get('fullName'))
        # add the team to the dictionary
        player.update({'Team': target_club})

        # change the player category key to be a string instead of a list
        cat_string = ''
        for i in player.get('playerCategories'):
            cat_string = cat_string + i
        player.update({'playerCategories': cat_string})

        # check player status for loan options and update if on loan
        for i in player.get('playerStatusList'):
            if i == 'Loaned Out':
                player.update({'onLoan': True})

        # pull the slug for building the url, and drop all the data we don't care about
        url_addon = player.get('playerSlug')
        for drop in dict_drop:
            player.pop(drop)

        # link to player's page is /players/slug
        # have to use selenium because there are dynamic components that have to render with js
        player_url = base_url + "/players/" + url_addon + "/"
        driver = webdriver.Chrome()
        driver.get(player_url)
        sleep(5)
        overall_player_page = driver.page_source

        # with the full html, pull the player stats data
        player_soup = bs(overall_player_page, "html.parser")
        player_data = player_soup.find("div", class_="mls-opta--season-player-stats")
        combo_data = player_data.find_all("div", class_="Opta-Stat")

        # stats data comes through as combined text of the value and key, so split it all out
        s = 0
        for i in combo_data:
            data = i.get_text()

            # if it is a success rate, we have to specify which success rate it is (same order every time)
            if data.find('Success rate') >= 0:
                if player.get('position') == 'Goalkeeper':
                    key_value = 'Success Rate - ' + success_list_gk[s]
                else:
                    key_value = 'Success Rate - ' + success_list[s]
                data_value = data[0:data.find('Success rate')]
                s += 1
                player.update({key_value: data_value})

            # if it is pass direction %, split it out into four separate key/value pairs
            elif data.find('Forward') >= 0:
                forward_value = data[0:data.find('Forward')] + '%'
                left_value = data[(data.find('Forward') + len('Forward')):data.find('Left')] + '%'
                right_value = data[(data.find('Left') + len('Left')):data.find('Right')] + '%'
                back_value = data[(data.find('Right') + len('Right')):data.find('Backward')] + '%'
                player.update({'Pass Direction - Forward': forward_value})
                player.update({'Pass Direction - Left': left_value})
                player.update({'Pass Direction - Right': right_value})
                player.update({'Pass Direction - Back': back_value})

            # if it is passing accuracy by area %, split it into separate key/value pairs by half
            elif data.find('Opp. half') >= 0:
                opp_value = data[0:data.find('Opp. half')] + '%'
                own_value = data[(data.find('Opp. half') + len('Opp. half')):data.find('Own half')] + '%'
                player.update({'Pass Accuracy - Opp. Half': opp_value})
                player.update({'Pass Accuracy - Own Half': own_value})

            # otherwise, split the data using the standard split function built above
            else:
                for d in data_list:
                    player = split_data(data, d, True, player)
                for d in data_list_flip:
                    player = split_data(data, d, False, player)

        # create a new dataframe with the new player data, concatenate on to the full data frame
        new_data = pd.DataFrame(player, index=['i', ])
        all_data = pd.concat([all_data, new_data], ignore_index=True)
        all_data.to_csv('player_data.csv', index=False, encoding='utf-8-sig')
