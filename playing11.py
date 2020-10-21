from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify, request
import datetime
import base64
import os
import multiprocessing
import operator

app = Flask(__name__)

directory = os.path.dirname(__file__)


@app.route('/home')
def home():
    return render_template('/home.html')


@app.route('/submit/<string:name>/<int:type>/<string:year>', methods=['GET', 'POST'])
def submit(name, type, year):
    print(datetime.datetime.now())
    #batting_result = best_batsmen(name, type, year)
    name = name.replace('|','/')
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    return_dict1 = manager.dict()
    #batting_details = {}
    #jobs = []
    p1 = multiprocessing.Process(target=best_batsmen, args=(name, type, year, return_dict))
    p2 = multiprocessing.Process(target=best_bowlers, args=(name, type, year, return_dict1))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    #bowling_result = best_bowlers(name, type, year)
    #print(bowling_result, len(bowling_result))
    return_dict.update(return_dict1)
    print(return_dict, len(return_dict))
    print(datetime.datetime.now())
    if request.method == "GET":
        return jsonify(return_dict)
    elif request.method == "POST":
        return render_template('submit.html', final_players=return_dict, match_type=type, year=year)
    else:
        return "Invalid Action"


def best_avg_sr(url, player_name):
    url_data = requests.get(url)
    soup = BeautifulSoup(url_data.text, 'html.parser')
    table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
    if table_cont is not None:
        for tr in table_cont:
            tds = tr.find_all('td')
            player = tds[0].a.get_text()
            if player == player_name:
                return 0
            else:
                continue
    return 1


def best_economy(url, player_name):
    player_economy = {}
    url_data = requests.get(url)
    soup = BeautifulSoup(url_data.text, 'html.parser')
    table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
    if table_cont is not None:
        for tr in table_cont:
            tds = tr.find_all('td')
            player = tds[0].a.get_text()
            economy = tds[5].get_text()
            if player == player_name:
                if player not in player_economy.keys():
                    player_economy = {
                        player: {
                            'Bowler': player,
                            'Eco': float(economy)
                        }
                    }
                else:
                    player_economy[player]['Bowler'] = player
                    player_economy[player]['Eco'] = float(player_economy['Eco']) + float(economy)
                return 0, player_economy
            else:
                continue
    return 1, player_economy


def best_batsmen(name, type, year, batting_details):
    teamname = name.split('/')
    playing_11 = []
    not_playing_11 = []
    years = year.split('-')
    if years[0] > years[1]:
        no_years = years[0]
        min_years = years[1]
    else:
        no_years = years[1]
        min_years = years[0]
    match_type = ''
    if type == 1:
        match_type = 'Test'
    elif type == 2:
        match_type = 'ODI'
    elif type == 3:
        match_type = 'T20'
    #global batting_details
    player_list = []
    player_count = 0
    lv_ret = 0
    lv_return = 0
    for i in reversed(range(int(no_years) + 1)):
        if i < int(min_years):
            break
        url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/most-runs/' + str(type) + '/' + str(
            i) + '/all/'
        #print(url)
        url_data = requests.get(url)
        soup = BeautifulSoup(url_data.text, 'html.parser')
        try:
            table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
        except:
            continue
        #print(table_cont)
        if table_cont is not None:
            for tr in table_cont:
                tds = tr.find_all('td')
                player = tds[0].a.get_text()
                #image_page = tds[0].a.get('href')
                matches = tds[1].get_text()
                innings = tds[2].get_text()
                runs = tds[3].get_text()
                runs = runs.replace(',', '')
                avg = tds[4].get_text()
                sr = tds[5].get_text()
                #four = tds[6].get_text()
                #six = tds[7].get_text()
                '''Check if player is in best avg list and best strike rate list'''
                avg_url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/highest-avg/' + str(
                    type) + '/' + str(i) + '/all'
                lv_return = best_avg_sr(avg_url, player)
                sr_url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/highest-sr/' + str(
                    type) + '/' + str(i) + '/all'
                lv_ret = best_avg_sr(sr_url, player)
                if (match_type != 'Test' and lv_return == 0 and lv_ret == 0) or (match_type == 'Test' and lv_return == 0):
                    player_list.append(player)
                    if player not in batting_details.keys():
                        batting_details[player] = {
                            'Match type': match_type,
                            'Year': year,
                            'Team': teamname[0],
                            'Player name': player,
                            'Matches': int(matches),
                            'Innings': int(innings),
                            'Runs': int(runs),
                            'Average': float(avg),
                            'Strike rate': float(sr),
                            'Role': 'Batsman'
                        }
                    else:
                        batting_details[player] = {
                            'Match type': match_type,
                            'Year': year,
                            'Team': teamname[0],
                            'Player name': player,
                            'Matches': int(batting_details[player]['Matches']) + int(matches),
                            'Innings': int(batting_details[player]['Innings'])+ int(innings),
                            'Runs': int(batting_details[player]['Runs']) + int(runs),
                            'Average': round(float(batting_details[player]['Average']) + float(avg), 2),
                            'Strike rate': round(float(
                            batting_details[player]['Strike rate']) + float(sr), 2),
                            'Role': 'Batsman'
                        }
                        # batting_details[player]['Match type'] = match_type
                        # batting_details[player]['Year'] = year
                        # batting_details[player]['Player name'] = player
                        # batting_details[player]['Role'] = 'Batsman'
                        # batting_details[player]['Matches'] = int(batting_details[player]['Matches']) + int(matches)
                        # batting_details[player]['Innings'] = int(batting_details[player]['Innings']) + int(innings)
                        # batting_details.update({player: {'Runs': int(batting_details[player]['Runs']) + int(runs)}})
                        # print(batting_details)
                        # batting_details[player]['Average'] = round(float(batting_details[player]['Average']) + float(avg), 2)
                        # batting_details[player]['Strike rate'] = round(float(
                        #     batting_details[player]['Strike rate']) + float(sr), 2)
                else:
                    continue
        # print(batting_details)
    player_list_copy = player_list.copy()
    #print(player_list_copy)
    # print(set(player_list))
    for players in set(player_list):
        for copy_players in player_list_copy:
            if players == copy_players:
                player_count += 1
        # print(players, "no of years played: ",player_count)
        batting_details[players] = {
            'Match type': batting_details[players]['Match type'],
            'Year': batting_details[players]['Year'],
            'Team': teamname[0],
            'Player name': players,
            'Matches': batting_details[players]['Matches'],
            'Innings': batting_details[players]['Innings'],
            'Runs': batting_details[players]['Runs'],
            'Average': round(batting_details[players]['Average'] / player_count, 2),
            'Strike rate': round(batting_details[players]['Strike rate'] / player_count, 2),
            'Role': 'Batsman'
        }
        #batting_details[players]['Average'] = batting_details[players]['Average'] / player_count
        #batting_details[players]['Strike rate'] = batting_details[players]['Strike rate'] / player_count
        player_count = 0
        # print(batting_details)
        if batting_details[players]['Match type'] == 'ODI' and batting_details[players]['Average'] >= 40 and batting_details[players]['Strike rate'] >= 85:
            playing_11.append(players)
            continue
        elif batting_details[players]['Match type'] == 'Test' and batting_details[players]['Average'] >= 40:
            playing_11.append(players)
            continue
        elif batting_details[players]['Match type'] == 'T20' and batting_details[players]['Average'] >= 25 and batting_details[players]['Strike rate'] >= 100:
            playing_11.append(players)
            continue
        else:
            not_playing_11.append(players)
            # print(playing_11)
            # print(playing_11)
    #print(len(batting_details))
    for each_player in not_playing_11:
        if len(batting_details) > 7:
            del batting_details[each_player]
    # render_template('/submit.html', name=name, type=type, years=year)
    print(batting_details, len(batting_details))


def best_bowlers(name, type, year, batting_details):
    teamname = name.split('/')
    playing_11 = []
    not_playing_11 = []
    match_type = ''
    years = year.split('-')
    if years[0] > years[1]:
        no_years = years[0]
        min_years = years[1]
    else:
        no_years = years[1]
        min_years = years[0]

    if type == 1:
        match_type = 'Test'
    elif type == 2:
        match_type = 'ODI'
    elif type == 3:
        match_type = 'T20'
    #global batting_details
    player_economy = {}
    player_list = []
    player_count = 0
    for i in reversed(range(int(no_years) + 1)):
        if i < int(min_years):
            break
        url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/most-wickets/' + str(type) + '/' + str(i) + '/all/'
        url_data = requests.get(url)
        soup = BeautifulSoup(url_data.text, 'html.parser')
        try:
            table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
        except:
            continue
        if table_cont is not None:
            for tr in table_cont:
                tds = tr.find_all('td')
                player = tds[0].a.get_text()
                #image_page = tds[0].a.get('href')
                matches = tds[1].get_text()
                overs = tds[2].get_text()
                balls = tds[3].get_text()
                balls = balls.replace(',', '')
                wckts = tds[4].get_text()
                avg = tds[5].get_text()
                runs = tds[6].get_text()
                runs = runs.replace(',', '')
                #four_w = tds[7].get_text()
                #five_w = tds[8].get_text()
                '''Check if player is in best avg list and best strike rate list'''
                avg_url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/lowest-avg/' + str(type) + '/' + str(i) + '/all'
                lv_return = best_avg_sr(avg_url, player)

                sr_url = 'https://www.cricbuzz.com/cricket-team/'+name+'/stats-table/lowest-econ/' + str(type) + '/' + str(i) + '/all'
                lv_ret , player_economy = best_economy(sr_url, player)
                #print(player_economy)
                if lv_return == 0 or lv_ret == 0:
                    player_list.append(player)
                    if player not in batting_details.keys():
                        #print(player_economy)
                        batting_details[player] = {
                            'Match type': match_type,
                            'Year': year,
                            'Team': teamname[0],
                            'Player name': player,
                            'Matches': int(matches),
                            'Overs': int(overs),
                            'Balls': int(balls),
                            'Wickets': int(wckts),
                            'Average': float(avg),
                            'Eco': player_economy[player]['Eco'],
                            'Runs': int(runs),
                            'Role': 'Bowler'
                        }
                    else:
                        batting_details[player] = {
                            'Match type': match_type,
                            'Year': year,
                            'Team': teamname[0],
                            'Player name': player,
                            'Matches': int(batting_details[player]['Matches']) + int(matches),
                            'Overs': int(batting_details[player]['Overs']) + int(overs),
                            'Balls': int(batting_details[player]['Balls']) + int(balls),
                            'Wickets': int(batting_details[player]['Wickets']) + int(wckts),
                            'Average': round(float(batting_details[player]['Average']) + float(avg), 2),
                            'Eco': round(batting_details[player]['Eco'] + player_economy[player]['Eco'], 2),
                            'Runs': int(batting_details[player]['Runs']) + int(runs),
                            'Role': 'Bowler'
                        }
                        # batting_details[player]['Match type'] = match_type
                        # batting_details[player]['Year'] = year
                        # batting_details[player]['Player name'] = player
                        # batting_details[player]['Role'] = 'Bowler'
                        # batting_details[player]['Matches'] = int(batting_details[player]['Matches']) + int(matches)
                        # batting_details[player]['Overs'] = int(batting_details[player]['Overs']) + int(overs)
                        # batting_details[player]['Balls'] = int(batting_details[player]['Balls']) + int(balls)
                        # batting_details[player]['Wickets'] = int(batting_details[player]['Wickets']) + int(wckts)
                        # batting_details[player]['Average'] = round(float(batting_details[player]['Average']) + float(avg), 2)
                        # batting_details[player]['Eco'] = round(batting_details[player]['Eco'] + player_economy[player]['Eco'], 2)
                        # batting_details[player]['Runs'] = int(batting_details[player]['Runs']) + int(runs)
                else:
                    continue
        # print(batting_details)
    #print(batting_details)
    player_list_copy = player_list.copy()
    # print(player_list_copy)
    # print(set(player_list))
    for players in set(player_list):
        for copy_players in player_list_copy:
            if players == copy_players:
                player_count += 1
        # print(players, "no of years played: ",player_count)
        batting_details[players] = {
            'Match type': batting_details[players]['Match type'],
            'Year': batting_details[players]['Year'],
            'Team': teamname[0],
            'Player name': players,
            'Matches': batting_details[players]['Matches'],
            'Overs': batting_details[players]['Overs'],
            'Balls': batting_details[players]['Balls'],
            'Wickets': batting_details[players]['Wickets'],
            'Average': round(batting_details[players]['Average'] / player_count, 2),
            'Eco': round(batting_details[players]['Eco'] / player_count, 2),
            'Runs': batting_details[players]['Runs'],
            'Role': 'Bowler'
        }
        #batting_details[players]['Average'] = batting_details[players]['Average'] / player_count
        #batting_details[players]['Eco'] = batting_details[players]['Eco'] / player_count
        player_count = 0
        # print(batting_details)
        if batting_details[players]['Match type'] == 'ODI' and batting_details[players]['Average'] <= 50 and batting_details[players]['Eco'] < 6:
            playing_11.append(players)
            continue
        elif batting_details[players]['Match type'] == 'Test' and batting_details[players]['Average'] <= 40 and batting_details[players]['Eco'] <= 3.5:
            playing_11.append(players)
            continue
        elif batting_details[players]['Match type'] == 'T20' and batting_details[players]['Average'] <= 32 and batting_details[players]['Eco'] <= 8:
            playing_11.append(players)
            continue
        else:
            not_playing_11.append(players)
            # print(playing_11)
            # print(playing_11)

    #print(len(batting_details))
    for each_player in not_playing_11:
        if len(batting_details) > 6:
            del batting_details[each_player]
    # render_template('/submit.html', name=name, type=type, years=year)


if __name__ == '__main__':
    app.run(debug=True)