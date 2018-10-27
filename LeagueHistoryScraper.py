from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import sys


#http request methods from https://realpython.com/python-web-scraping-practical-introduction/    
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def scrape_boxscore(league_id, year, week, team):
    boxscore_url = 'http://games.espn.com/ffl/boxscorequick?leagueId={leagueId}&teamId={teamId}&scoringPeriodId={week}&seasonId={season}&view=scoringperiod&version=quick'.format(leagueId=league_id,teamId=str(team),week=str(week),season=str(year))    
                
    #print boxscore_url

    raw_html = simple_get(boxscore_url)

    if (raw_html):

        html = BeautifulSoup(raw_html, 'html.parser')
        team_inf = html.find("div", {"id": "teamInfos"})
        if(team_inf):
            team_inf = team_inf.find_all("div", recursive=False)

            opponent_info = team_inf[1].find("b")
            opponent = "BYE"
            if (opponent_info):
                opponent = opponent_info.text

            score = 0
            if (year < 2017):
                score = float(html.find("tr", {"class": "playerTableBgRowTotals"}).find("td", {"class": "appliedPoints"}).text)
            else:
                score = float(html.find("div", {"class": "totalScore"}).text)

            boxscore = {
                "teamId": team, 
                "teamName": team_inf[0].find("b").text, 
                "opponentName": opponent, 
                "score": score,
                "url": boxscore_url,
                "players": []
                }

            html_players = html.find("table", {"class":"playerTableTable"}).find_all("tr",{"class":"pncPlayerRow"})
            for html_player in html_players:
                name_position = html_player.find("td", {"class": "playertablePlayerName"}).text.split(u'\xa0')        
                boxscore["players"].append({"name": name_position[0], "position": name_position[1], "points": float(html_player.find("td",{"class":"appliedPoints"}).text)})

            return boxscore
    
    return None

def get_league_history(league_id, year_range, week_range, team_range):

    league_history = {
        "league_id": league_id,
        "seasons": []
    }

    for year in year_range: # should be 2019

        season = {
            "year": year,
            "weeks": []
        }

        for weekNumber in week_range: # should be 17

            week = {
                "weekNumber": weekNumber,
                "boxscores": []
            }

            for team_id in team_range: # should be 17            

                boxscore = scrape_boxscore(league_id, year, weekNumber, team_id )
                print str(year) + " " + str(weekNumber) + " " + str(team_id)
                if (boxscore):
                    week["boxscores"].append(boxscore)

            season["weeks"].append(week)

        league_history["seasons"].append(season)

    with open('{league_id}.json'.format(league_id=league_id), 'w') as fp:
        json.dump(league_history, fp, sort_keys=True, indent=4)