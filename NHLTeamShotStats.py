import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.request import urlopen
import json
from datetime import date
from collections import OrderedDict


url = 'https://statsapi.web.nhl.com/api/v1/teams/'
team_shot_stats_dict = {}
team_goal_stats_dict = {}
team_shots_per_goal_dict = {}

for x in range(1,55):
	if x == 11 or x == 27 or 30<x<52: #excluding non-team ids
		continue
	http_response_stream = urlopen(url + str(x) + '/stats')
	http_json = http_response_stream.read()
	http_response_stream.close()
	team_info_dict = json.loads(http_json)
	team_stats_dict = team_info_dict['stats'][0]['splits'][0]
	goals_per_game = team_stats_dict['stat']['goalsPerGame']
	shots_per_game = team_stats_dict['stat']['shotsPerGame']
	team_name = team_stats_dict['team']['name']
	team_shot_stats_dict.update({team_name : shots_per_game})
	team_goal_stats_dict.update({team_name : goals_per_game})
	team_shots_per_goal_dict.update({team_name : shots_per_game/goals_per_game})

	print('Downloading ' + team_name + ' stats \n')

scope = ['https://www.googleapis.com/auth/drive', 
'https://www.googleapis.com/auth/spreadsheets']

credentials = ServiceAccountCredentials.from_json_keyfile_name('Fantasy Hockey Goalie Stats-a52cfb36fdfb.json', scope)
google_client = gspread.authorize(credentials)

date = str(date.today())
spreadsheet = google_client.create('NHL Team Shot Stats ' + date)
sheet = spreadsheet.sheet1

sheet.append_row(['Teams', 'Shots/Game', 'Goals/Game', 'Shots/Goal', 'Rank'])

def take_value(elem):
    return elem[1]

rank = 1

for key, value in sorted(team_shots_per_goal_dict.items(), key=take_value, reverse=False):

	sheet.append_row([key, team_shot_stats_dict[key], team_goal_stats_dict[key], value, rank])
	print('Uploading ' + key + '\t' + str(team_shot_stats_dict[key]) + '\t' + str(team_goal_stats_dict[key]) + '\t' + str(team_shots_per_goal_dict[key]) + ' \t Rank: ' + str(rank) + '\n')
	rank += 1

spreadsheet.share('mcintojj@gmail.com', perm_type='user', role='writer')