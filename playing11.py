from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify, request
import datetime
import base64
import os
import operator

app = Flask(__name__)

directory = os.path.dirname(__file__)

@app.route('/home')
def home():
    return render_template('/home.html')


@app.route('/submit/<string:name>/<int:type>/<string:year>', methods=['GET', 'POST'])
def submit(name, type, year):
    print(datetime.datetime.now())
    batting_result = best_batsmen(name, type, year)
    print("--------------------------------------------------")
    print(batting_result, len(batting_result))
    bowling_result = best_bowlers(name, type, year)
    print(bowling_result, len(bowling_result))
    batting_result.update(bowling_result)
    print(batting_result, len(batting_result))
    if request.method == "GET":
        return jsonify(batting_result)
    elif request.method == "POST":
        return render_template('submit.html', final_players=batting_result)
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


def best_batsmen(name, type, year):
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
                image_page = tds[0].a.get('href')
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
                        '''Getting palyer profile pic'''
                        page_data = requests.get('https://www.cricbuzz.com' + image_page)
                        image_soup = BeautifulSoup(page_data.text, 'html.parser')
                        image = image_soup.find('img', {'title': 'profile image'})
                        image_url = image.get('src')
                        image_data = requests.get('https://www.cricbuzz.com' + image_url)
                        print(image_data.content)
                        encoded_img = base64.b64encode(image_data.content)
                        pathname = directory + "/static/India/" + player + ".jpg"
                        with open(pathname, 'wb') as f:
                            decoded_image_data = base64.decodebytes(encoded_img)
                            f.write(decoded_image_data)
                        '''end of downloading images'''
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
                                'Role': 'Batsman',
                                '4s': four,
                                '6s': six
                            }
                        else:
                            batting_details[player]['Match type'] = match_type
                            batting_details[player]['Year'] = year
                            batting_details[player]['Player name'] = player
                            batting_details[player]['4s'] = four
                            batting_details[player]['6s'] = six
                            batting_details[player]['Role'] = 'Batsman'
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
        if len(batting_details) > 7:
            del batting_details[each_player]
    # for key in batting_details.items():
    print(datetime.datetime.now())
    # render_template('/submit.html', name=name, type=type, years=year)
    return batting_details


def best_bowlers(name, type, year):
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
    batting_details = {}
    player_economy = {}
    player_list = []
    player_flag = 1
    player_count = 0
    for i in reversed(range(int(no_years) + 1)):
        if i < int(min_years):
            break
        url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/most-wickets/' + str(type) + '/' + str(i) + '/all/'
        url_data = requests.get(url)
        soup = BeautifulSoup(url_data.text, 'html.parser')
        table_cont = soup.find_all('tbody')[0].find_all('tr', {'class': 'cb-srs-stats-tr'})
        if table_cont is not None:
            for tr in table_cont:
                tds = tr.find_all('td')
                player = tds[0].a.get_text()
                image_page = tds[0].a.get('href')
                matches = tds[1].get_text()
                overs = tds[2].get_text()
                balls = tds[3].get_text()
                balls = balls.replace(',', '')
                wckts = tds[4].get_text()
                avg = tds[5].get_text()
                runs = tds[6].get_text()
                runs = runs.replace(',', '')
                four_w = tds[7].get_text()
                five_w = tds[8].get_text()
                '''Check if player is in best avg list and best strike rate list'''
                avg_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/lowest-avg/' + str(type) + '/' + str(i) + '/all'
                lv_return = best_avg_sr(avg_url, player)

                sr_url = 'https://www.cricbuzz.com/cricket-team/India/2/stats-table/lowest-econ/' + str(type) + '/' + str(i) + '/all'
                lv_ret , player_economy = best_economy(sr_url, player)
                #print(player_economy)
                if lv_return == 0 or lv_ret == 0:
                    player_list.append(player)
                    '''Getting palyer profile pic'''
                    page_data = requests.get('https://www.cricbuzz.com'+image_page)
                    image_soup = BeautifulSoup(page_data.text, 'html.parser')
                    image = image_soup.find('img', {'title': 'profile image'})
                    image_url = image.get('src')
                    image_data = requests.get('https://www.cricbuzz.com'+image_url)
                    print(image_data.content)
                    encoded_img = base64.b64encode(image_data.content)
                    pathname = directory+"/static/India/"+player+".jpg"
                    with open(pathname, 'wb') as f:
                        decoded_image_data = base64.decodebytes(encoded_img)
                        f.write(decoded_image_data)
                    if player not in batting_details.keys():
                        player_flag = 1
                        #print(player_economy)
                        batting_details[player] = {
                            'Match type': match_type,
                            'Year': year,
                            'Player name': player,
                            'Matches': int(matches),
                            'Overs': int(overs),
                            'Balls': int(balls),
                            'Wickets': int(wckts),
                            'Average': float(avg),
                            'Eco': player_economy[player]['Eco'],
                            'Runs': int(runs),
                            'Role': 'Bowler',
                            '4Fers': int(four_w),
                            '5Fers': int(five_w)
                        }
                    else:
                        batting_details[player]['Match type'] = match_type
                        batting_details[player]['Year'] = year
                        batting_details[player]['Player name'] = player
                        batting_details[player]['Role'] = 'Bowler'
                        batting_details[player]['Matches'] = int(batting_details[player]['Matches']) + int(matches)
                        batting_details[player]['Overs'] = int(batting_details[player]['Overs']) + int(overs)
                        batting_details[player]['Balls'] = int(batting_details[player]['Balls']) + int(balls)
                        batting_details[player]['Wickets'] = int(batting_details[player]['Wickets']) + int(wckts)
                        batting_details[player]['Average'] = float(batting_details[player]['Average']) + float(avg)
                        batting_details[player]['Eco'] = batting_details[player]['Eco'] + player_economy[player]['Eco']
                        batting_details[player]['Runs'] = int(batting_details[player]['Runs']) + int(runs)
                        batting_details[player]['4Fers'] = int(batting_details[player]['4Fers']) + int(four_w)
                        batting_details[player]['5Fers'] = int(batting_details[player]['5Fers']) + int(five_w)

                        player_flag += 1
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
        batting_details[players]['Average'] = batting_details[players]['Average'] / player_count
        batting_details[players]['Eco'] = batting_details[players]['Eco'] / player_count
        player_count = 0
        # print(batting_details)
        if batting_details[players]['Average'] <= 50 and batting_details[players]['Eco'] < 6:
            playing_11.append(players)
            continue
        else:
            not_playing_11.append(players)
            # print(playing_11)
            # print(playing_11)
    print(batting_details)
    print(len(batting_details))
    for each_player in not_playing_11:
        if len(batting_details) > 6:
            del batting_details[each_player]
    # for key in batting_details.items():
    print(datetime.datetime.now())
    # render_template('/submit.html', name=name, type=type, years=year)
    return batting_details


if __name__ == '__main__':
    app.run(debug=True)
