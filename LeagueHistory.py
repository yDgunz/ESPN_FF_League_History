from espnff import League

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

league_id = 552541
year = 2018
league = League(552541, 2018)

current_teams = league.teams
champions = []

# get this year's teams and their current records
for team in current_teams:
    team.seasons = [{"year": 2018, "wins": team.wins, "losses": team.losses, "points_for": team.points_for, "points_against": team.points_against}]

# get all time records for each team
for year in range(2017,2009,-1):

    league = League(552541, year)

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
    team.championships = sum(1 for x in champions if x["team_id"] == team.team_id)
    print team.owner + " " + str(team.all_time_record["wins"]) + "-" + str(team.all_time_record["losses"]) + " " + str(team.championships)

template_data = {"teams": current_teams}

f = open("LeagueHistory.html", "w")
f.write(html_template.render(template_data))