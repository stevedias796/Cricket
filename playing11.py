from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify
import datetime
import operator

app = Flask(__name__)


@app.route('/home')
def home():
    render_template('/home.html')


@app.route('/submit/<string:name>/<int:type>/<string:year>', methods=['GET', 'POST'])
def submit(name, type, year):
    print(datetime.datetime.now())
    playing_11 = []
    not_playing_11 = []
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
    batting_details = {}
    player_list = []
    player_flag = 1
    player_count = 0
    for i in reversed(range(int(no_years)+1)):
        if i < int(min_years):
            break
        url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/most-runs/'+str(type)+'/'+str(i)+'/all/'
        url_data = requests.get(url)
        soup = BeautifulSoup(url_data.text, 'html.parser')
        table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
        if table_cont is not None:
            for tr in table_cont:
                tds = tr.find_all('td')
                player = tds[0].a.get_text()
                matches = tds[1].get_text()
                innings = tds[2].get_text()
                runs = tds[3].get_text()
                runs = runs.replace(',', '')
                avg = tds[4].get_text()
                sr = tds[5].get_text()
                four = tds[6].get_text()
                six = tds[7].get_text()
                '''Check if player is in best avg list and best strike rate list'''
                avg_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/highest-avg/'+str(type)+'/'+str(i)+'/all'
                lv_return = best_avg_sr(avg_url, player)
                if lv_return == 0:
                    sr_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/highest-sr/'+str(type)+'/'+str(i)+'/all'
                    lv_ret = best_avg_sr(sr_url, player)
                    if lv_ret == 0:
                        player_list.append(player)
                        if player not in batting_details.keys():
                            player_flag = 1
                            batting_details[player] = {
                                'Match type': match_type,
                                'Year': year,
                                'Player name': player,
                                'Matches': int(matches),
                                'Innings': int(innings),
                                'Runs': int(runs),
                                'Average': float(avg),
                                'Strike rate': float(sr),
                                '4s': four,
                                '6s': six
                            }
                        else:
                            batting_details[player]['Match type'] = match_type
                            batting_details[player]['Year'] = year
                            batting_details[player]['Player name'] = player
                            batting_details[player]['4s'] = four
                            batting_details[player]['6s'] = six
                            batting_details[player]['Matches'] = int(batting_details[player]['Matches']) + int(matches)
                            batting_details[player]['Innings'] = int(batting_details[player]['Innings']) + int(innings)
                            batting_details[player]['Runs'] = int(batting_details[player]['Runs']) + int(runs)
                            batting_details[player]['Average'] = float(batting_details[player]['Average']) + float(avg)
                            batting_details[player]['Strike rate'] = float(batting_details[player]['Strike rate']) + float(sr)
                            player_flag += 1
                else:
                    continue
        #print(batting_details)
    player_list_copy = player_list.copy()
    #print(player_list_copy)
    #print(set(player_list))
    for players in set(player_list):
        for copy_players in player_list_copy:
            if players == copy_players:
                player_count += 1
        #print(players, "no of years played: ",player_count)
        batting_details[players]['Average'] = batting_details[players]['Average']/player_count
        batting_details[players]['Strike rate'] = batting_details[players]['Strike rate'] / player_count
        player_count = 0
        #print(batting_details)
        if batting_details[players]['Average'] >= 40 and batting_details[players]['Strike rate'] >= 85:
            playing_11.append(players)
            continue
        else:
            not_playing_11.append(players)
            #print(playing_11)
            #print(playing_11)
    print(batting_details)
    print(len(batting_details))
    for each_player in not_playing_11:
        del batting_details[each_player]
    #for key in batting_details.items():
    print(datetime.datetime.now())
    #render_template('/submit.html', name=name, type=type, years=year)
    return jsonify(batting_details)


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


def best_batsmen():
    playing_11 = []
    not_playing_11 = []
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
    batting_details = {}
    player_list = []
    player_flag = 1
    player_count = 0
    for i in reversed(range(int(no_years) + 1)):
        if i < int(min_years):
            break
        url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/most-runs/' + str(type) + '/' + str(
            i) + '/all/'
        url_data = requests.get(url)
        soup = BeautifulSoup(url_data.text, 'html.parser')
        table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
        if table_cont is not None:
            for tr in table_cont:
                tds = tr.find_all('td')
                player = tds[0].a.get_text()
                matches = tds[1].get_text()
                innings = tds[2].get_text()
                runs = tds[3].get_text()
                runs = runs.replace(',', '')
                avg = tds[4].get_text()
                sr = tds[5].get_text()
                four = tds[6].get_text()
                six = tds[7].get_text()
                '''Check if player is in best avg list and best strike rate list'''
                avg_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/highest-avg/' + str(
                    type) + '/' + str(i) + '/all'
                lv_return = best_avg_sr(avg_url, player)
                if lv_return == 0:
                    sr_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/highest-sr/' + str(
                        type) + '/' + str(i) + '/all'
                    lv_ret = best_avg_sr(sr_url, player)
                    if lv_ret == 0:
                        player_list.append(player)
                        if player not in batting_details.keys():
                            player_flag = 1
                            batting_details[player] = {
                                'Match type': match_type,
                                'Year': year,
                                'Player name': player,
                                'Matches': int(matches),
                                'Innings': int(innings),
                                'Runs': int(runs),
                                'Average': float(avg),
                                'Strike rate': float(sr),
                                '4s': four,
                                '6s': six
                            }
                        else:
                            batting_details[player]['Match type'] = match_type
                            batting_details[player]['Year'] = year
                            batting_details[player]['Player name'] = player
                            batting_details[player]['4s'] = four
                            batting_details[player]['6s'] = six
                            batting_details[player]['Matches'] = int(batting_details[player]['Matches']) + int(matches)
                            batting_details[player]['Innings'] = int(batting_details[player]['Innings']) + int(innings)
                            batting_details[player]['Runs'] = int(batting_details[player]['Runs']) + int(runs)
                            batting_details[player]['Average'] = float(batting_details[player]['Average']) + float(avg)
                            batting_details[player]['Strike rate'] = float(
                                batting_details[player]['Strike rate']) + float(sr)
                            player_flag += 1
                else:
                    continue
        # print(batting_details)
    player_list_copy = player_list.copy()
    # print(player_list_copy)
    # print(set(player_list))
    for players in set(player_list):
        for copy_players in player_list_copy:
            if players == copy_players:
                player_count += 1
        # print(players, "no of years played: ",player_count)
        batting_details[players]['Average'] = batting_details[players]['Average'] / player_count
        batting_details[players]['Strike rate'] = batting_details[players]['Strike rate'] / player_count
        player_count = 0
        # print(batting_details)
        if batting_details[players]['Average'] >= 40 and batting_details[players]['Strike rate'] >= 85:
            playing_11.append(players)
            continue
        else:
            not_playing_11.append(players)
            # print(playing_11)
            # print(playing_11)
    print(batting_details)
    print(len(batting_details))
    for each_player in not_playing_11:
        del batting_details[each_player]
    # for key in batting_details.items():
    print(datetime.datetime.now())
    # render_template('/submit.html', name=name, type=type, years=year)
    return jsonify(batting_details)
if __name__ == '__main__':
    app.run(debug=True)