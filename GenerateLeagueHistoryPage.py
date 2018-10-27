from espnff import League
import json

import django
from django.conf import settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['.'],
    }
]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()
from django.template.loader import get_template
from django.template import Context
html_template = get_template('LeagueHistoryTemplate.html')

league_id = 118990 #552541
year = 2018
league = League(league_id, 2018)

current_teams = league.teams
champions = []
top_10_games = []

# get this year's teams and their current records
for team in current_teams:
    team.seasons = [{"year": 2018, "wins": team.wins, "losses": team.losses, "points_for": team.points_for, "points_against": team.points_against}]

# get all time records for each team
for year in range(2017,2009,-1):

    league = League(league_id, year)

    #find champion for this year
    final_game = league.scoreboard()[0]
    if (final_game.home_score > final_game.away_score):
        champions.append({"year": year, "team_id": final_game.home_team.team_id})
    else:
        champions.append({"year": year, "team_id": final_game.away_team.team_id})


    for team in league.teams:
        current_team = next((x for x in current_teams if x.team_id == team.team_id), None)        
        if (current_team):
            current_team.seasons.append({"year": year, "wins": team.wins, "losses": team.losses, "points_for": team.points_for, "points_against": team.points_against})

# compile all-time records for each team
for team in current_teams:
    team.all_time_record = {}
    for stat in ["wins", "losses", "points_for", "points_against"]:
        team.all_time_record[stat] = sum(x[stat] for x in team.seasons)
    team.all_time_record["win_percentage"] = 100*float(team.all_time_record["wins"])/float(team.all_time_record["wins"]+team.all_time_record["losses"])
    team.championships = sum(1 for x in champions if x["team_id"] == team.team_id)
    #print team.owner + " " + str(team.all_time_record["wins"]) + "-" + str(team.all_time_record["losses"]) + " " + str(team.championships)

# find top 10 scores in league history
with open('{league_id}.json'.format(league_id=league_id), 'r') as fp:
    boxscores = json.load(fp)

top_10_scores = []

for season in boxscores["seasons"]:
    for week in season["weeks"]:
        for boxscore in week["boxscores"]:
            boxscore['teamOwner'] = next((t.owner for t in current_teams if t.team_id == boxscore['teamId']), 'N/A')
            # hack for Kendig / Brittany owner issue
            if (boxscore['teamOwner'] == "Christopher Kendig"):
                boxscore['teamOwner'] = "Brittany Jokl"
            boxscore['season'] = season['year']
            boxscore['week'] = week['weekNumber']
            top_10_scores.append(boxscore)
            top_10_scores.sort(key=lambda k: k['score'], reverse = True)
            top_10_scores = top_10_scores[:10]

template_data = {"teams": current_teams, "top_10_scores": top_10_scores}

f = open("{league_id}_history.html".format(league_id=league_id), "w")
f.write(html_template.render(template_data))