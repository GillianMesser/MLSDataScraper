# Summary
I’m a big soccer fan, and I thought it would be interesting to dive in to some player data for my favorite MLS team (Orlando City) as well as the rest of the MLS.  I also wanted to try to learn some data scraping techniques, so I chose to scrape data from the MLS website (https://www.mlssoccer.com/) as opposed to using API’s from other sources to pull player data.  This code pulls available data for the current season to date for all players from all teams (reference https://www.mlssoccer.com/players/).  The code could be easily modified to scrape data from a specific team by removing the outer loop and specifying the ‘target_club’ variable.  Primarily due to the sleep() lines put in to avoid overloading the servers, the code can take several hours to complete.  For a simple example of data visualizations built from this raw data, reference (https://public.tableau.com/app/profile/gillian.werner/viz/MLSTeamAnalysis/TeamBreakout).


# What are the files?
main.py – this houses all of the code required to scrape player data from the mls website.
player_data.csv – this is the raw data compiled from the code as of July 3rd, 2023.  Note that the data only represents the current season up to the date the code was last run.


# What libraries are used?
Beautiful soup - https://www.crummy.com/software/BeautifulSoup/bs4/doc/ - used to parse most of the html used for scraping/navigating.
Selenium - https://selenium-python.readthedocs.io/index.html - used on specific pages to allow widgets to generate properly before pulling html to be parsed and used.
Requests - https://requests.readthedocs.io/en/latest/ - used to load various url’s for use with beautiful soup.
Time - https://docs.python.org/3/library/time.html - sleep method used to create short delays before requests are made to avoid server overload.
Json - https://docs.python.org/3/library/json.html - used to read table data.
Pandas - https://pandas.pydata.org/docs/ - used to create and concatenate data frames of player information to ultimately export a csv for analytics.
