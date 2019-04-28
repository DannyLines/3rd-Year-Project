import numpy as np
import pandas as pd

def isNumber(input):
    try:
        result = int(input)
    except Exception as e:
        return False
    return True
# This script had to remove games between teams which are no longer in the premier league
# Then had to assign numbers to each team

directory_path = "static/csv/gameData/"
file_path = directory_path + "fixedData.csv"
output_path = directory_path + "fixedData.csv"
fixture_data = pd.read_csv(file_path)

array_1_form = []
array_2_form = []
array_3_form = []
array_4_form = []
array_5_form = []
array_6_form = []
array_7_form = []
array_8_form = []
array_9_form = []
array_10_form = []
array_11_form = []
array_12_form = []
array_13_form = []
array_14_form = []
array_15_form = []
array_16_form = []
array_17_form = []
array_18_form = []
array_19_form = []
array_20_form = []
array_21_form = []
array_22_form = []
array_23_form = []
array_24_form = []
array_25_form = []
array_26_form = []
array_27_form = []
array_28_form = []
array_29_form = []
array_30_form = []
array_31_form = []
array_32_form = []
array_33_form = []
array_34_form = []
array_35_form = []
array_36_form = []

global team1_count
global team2_count
global team3_count
global team4_count
global team5_count
global team6_count
global team7_count
global team8_count
global team9_count
global team10_count
global team11_count
global team12_count
global team13_count
global team14_count
global team15_count
global team16_count
global team17_count
global team18_count
global team19_count
global team20_count
global team21_count
global team22_count
global team23_count
global team24_count
global team25_count
global team26_count
global team27_count
global team28_count
global team29_count
global team30_count
global team31_count
global team32_count
global team33_count
global team34_count
global team35_count
global team36_count

team1_count = 0
team2_count = 0
team3_count = 0
team4_count = 0
team5_count = 0
team6_count = 0
team7_count = 0
team8_count = 0
team9_count = 0
team10_count = 0
team11_count = 0
team12_count = 0
team13_count = 0
team14_count = 0
team15_count = 0
team16_count = 0
team17_count = 0
team18_count = 0
team19_count = 0
team20_count = 0
team21_count = 0
team22_count = 0
team23_count = 0
team24_count = 0
team25_count = 0
team26_count = 0
team27_count = 0
team28_count = 0
team29_count = 0
team30_count = 0
team31_count = 0
team32_count = 0
team33_count = 0
team34_count = 0
team35_count = 0
team36_count = 0

def getForm(team):
    form_depth = -6
    form = []
    if team == 1:
        global team1_count
        team1_count += 1.0
        print("TEAM 1 COUNT " + str(team1_count))
        form = [array_1_form[form_depth:], team1_count]
    elif team == 2:
        global team2_count
        team2_count += 1.0
        form = [array_2_form[form_depth:], team2_count]
    elif team == 3:
        global team3_count
        team3_count += 1.0
        form = [array_3_form[form_depth:], team3_count]
    elif team == 4:
        global team4_count
        team4_count += 1.0
        form = [array_4_form[form_depth:], team4_count]
    elif team == 5:
        global team5_count
        team5_count += 1.0
        form = [array_5_form[form_depth:], team5_count]
    elif team == 6:
        global team6_count
        team6_count += 1.0
        form = [array_6_form[form_depth:], team6_count]
    elif team == 7:
        global team7_count
        team7_count += 1.0
        form = [array_7_form[form_depth:], team7_count]
    elif team == 8:
        global team8_count
        team8_count += 1.0
        form = [array_8_form[form_depth:], team8_count]
    elif team == 9:
        global team9_count
        team9_count += 1.0
        form = [array_9_form[form_depth:], team9_count]
    elif team == 10:
        global team10_count
        team10_count += 1.0
        form = [array_10_form[form_depth:], team10_count]
    elif team == 11:
        global team11_count
        team11_count += 1.0
        form = [array_11_form[form_depth:], team11_count]
    elif team == 12:
        global team12_count
        team12_count += 1.0
        form = [array_12_form[form_depth:], team12_count]
    elif team == 13:
        global team13_count
        team13_count += 1.0
        form = [array_13_form[form_depth:], team13_count]
    elif team == 14:
        global team14_count
        team14_count += 1.0
        form = [array_14_form[form_depth:], team14_count]
    elif team == 15:
        global team15_count
        team15_count += 1.0
        form = [array_15_form[form_depth:], team15_count]
    elif team == 16:
        global team16_count
        team16_count += 1.0
        form = [array_16_form[form_depth:], team16_count]
    elif team == 17:
        global team17_count
        team17_count += 1.0
        form = [array_17_form[form_depth:], team17_count]
    elif team == 18:
        global team18_count
        team18_count += 1.0
        form = [array_18_form[form_depth:], team18_count]
    elif team == 19:
        global team19_count
        team19_count += 1.0
        form = [array_19_form[form_depth:], team19_count]
    elif team == 20:
        global team20_count
        team20_count += 1.0
        form = [array_20_form[form_depth:], team20_count]
    elif team == 21:
        global team21_count
        team21_count += 1.0
        form = [array_21_form[form_depth:], team21_count]
    elif team == 22:
        global team22_count
        team22_count += 1.0
        form = [array_22_form[form_depth:], team22_count]
    elif team == 23:
        global team23_count
        team23_count += 1.0
        form = [array_23_form[form_depth:], team23_count]
    elif team == 24:
        global team24_count
        team24_count += 1.0
        form = [array_24_form[form_depth:], team24_count]
    elif team == 25:
        global team25_count
        team25_count += 1.0
        form = [array_25_form[form_depth:], team25_count]
    elif team == 26:
        global team26_count
        team26_count += 1.0
        form = [array_26_form[form_depth:], team26_count]
    elif team == 27:
        global team27_count
        team27_count += 1.0
        form = [array_27_form[form_depth:], team27_count]
    elif team == 28:
        global team28_count
        team28_count += 1.0
        form = [array_28_form[form_depth:], team28_count]
    elif team == 29:
        global team29_count
        team29_count += 1.0
        form = [array_29_form[form_depth:], team29_count]
    elif team == 30:
        global team30_count
        team30_count += 1.0
        form = [array_30_form[form_depth:], team30_count]
    elif team == 31:
        global team31_count
        team31_count += 1.0
        form = [array_31_form[form_depth:], team31_count]
    elif team == 32:
        global team32_count
        team32_count += 1.0
        form = [array_32_form[form_depth:], team32_count]
    elif team == 33:
        global team33_count
        team33_count += 1.0
        form = [array_33_form[form_depth:], team33_count]
    elif team == 34:
        global team34_count
        team34_count += 1.0
        form = [array_34_form[form_depth:], team34_count]
    elif team == 35:
        global team35_count
        team35_count += 1.0
        form = [array_35_form[form_depth:], team35_count]
    elif team == 36:
        global team36_count
        team36_count += 1.0
        form = [array_36_form[form_depth:], team36_count]
    return form


def updateForm(data, team, result, isHome):
    goal_difference = 0
    if isHome:
        goal_difference = data['FTHG'] - data['FTAG']
        goals_for = data['FTHG']
        goals_against = data['FTAG']
    else:
        goal_difference = data['FTAG'] - data['FTHG']
        goals_for = data['FTAG']
        goals_against = data['FTHG']
    if(team == 1):
        array_1_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 2):
        array_2_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 3):
        array_3_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 4):
        array_4_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 5):
        array_5_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 6):
        array_6_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 7):
        array_7_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 8):
        array_8_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 9):
        array_9_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 10):
        array_10_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 11):
        array_11_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 12):
        array_12_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 13):
        array_13_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 14):
        array_14_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 15):
        array_15_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 16):
        array_16_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 17):
        array_17_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 18):
        array_18_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 19):
        array_19_form.append([result, goals_for, goals_against, goal_difference])
    elif team == 20:
        array_20_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 21):
        array_21_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 22):
        array_22_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 23):
        array_23_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 24):
        array_24_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 25):
        array_25_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 26):
        array_26_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 27):
        array_27_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 28):
        array_28_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 29):
        array_29_form.append([result, goals_for, goals_against, goal_difference])
    elif team == 30:
        array_30_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 31):
        array_31_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 32):
        array_32_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 33):
        array_33_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 34):
        array_34_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 35):
        array_35_form.append([result, goals_for, goals_against, goal_difference])
    elif (team == 36):
        array_36_form.append([result, goals_for, goals_against, goal_difference])

    return
count = 1.0

home_form_points_column = []
home_form_GA_column = []
home_form_GF_column = []
home_form_GD_column = []

form_points_dif = []
form_GA_dif = []
form_GF_dif = []
form_GD_dif = []


away_form_points_column = []
away_form_GA_column = []
away_form_GF_column = []
away_form_GD_column = []

for index, row in fixture_data.iterrows():
    default_string = "array_"
    if not count == 0:
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        result = row['FTR']

        home_form_GF = 0
        home_form_GA = 0
        home_form_GD = 0
        home_form_points = 0

        away_form_GF = 0
        away_form_GA = 0
        away_form_GD = 0
        away_form_points = 0

        if home_team != 0:
            home_result = getForm(home_team)
            form = home_result[0]
            home_team_match_count = home_result[1]
            for entry in form:
                home_form_GF += entry[1]
                home_form_GA += entry[2]
                home_form_GD += entry[3]
                if (entry[0] == 'W'):
                    home_form_points += 3
                elif (entry[0] == 'D'):
                    home_form_points += 1

        if away_team != 0:
            away_result = getForm(away_team)
            form = away_result[0]
            away_team_match_count = away_result[1]
            for entry in form:
                away_form_GF += entry[1]
                away_form_GA += entry[2]
                away_form_GD += entry[3]
                if (entry[0] == 'W'):
                    away_form_points += 3
                elif (entry[0] == 'D'):
                    away_form_points += 1
        try:
            print(home_team_match_count)
            print(home_form_points)
            print("counter - " + str(home_team_match_count-1.0))
            print("-----------")
            home_form_points_column.append(float(home_form_points)/(home_team_match_count-1))
            home_form_GF_column.append(float(home_form_GF)/(home_team_match_count-1))
            home_form_GA_column.append(float(home_form_GA)/(home_team_match_count-1))
            home_form_GD_column.append(float(home_form_GD)/(home_team_match_count-1))

            away_form_points_column.append(float(away_form_points)/(away_team_match_count-1))
            away_form_GF_column.append(float(away_form_GF)/(away_team_match_count-1))
            away_form_GA_column.append(float(away_form_GA)/(away_team_match_count-1))
            away_form_GD_column.append(float(away_form_GD)/(away_team_match_count-1))
        except ZeroDivisionError as e:
            home_form_points_column.append(float(home_form_points) / home_team_match_count)
            home_form_GF_column.append(float(home_form_GF) / home_team_match_count)
            home_form_GA_column.append(float(home_form_GA) / home_team_match_count)
            home_form_GD_column.append(float(home_form_GD) / home_team_match_count)

            away_form_points_column.append(float(away_form_points) / away_team_match_count)
            away_form_GF_column.append(float(away_form_GF) / away_team_match_count)
            away_form_GA_column.append(float(away_form_GA) / away_team_match_count)
            away_form_GD_column.append(float(away_form_GD) / away_team_match_count)
        try:
            form_points_dif.append(home_form_points_column[-1] - away_form_points_column[-1])
        except ZeroDivisionError as e:
            form_points_dif.append(0)
        try:
            form_GF_dif.append(home_form_GF_column[-1] - away_form_GF_column[-1])
        except ZeroDivisionError as e:
            form_GF_dif.append(0)
        try:
            form_GA_dif.append(home_form_GA_column[-1] - away_form_GA_column[-1])
        except ZeroDivisionError as e:
            form_GA_dif.append(0)
        try:
            form_GD_dif.append(home_form_GD_column[-1] - away_form_GD_column[-1])
        except ZeroDivisionError as e:
            form_GD_dif.append(0)


        if (result == 0):
            updateForm(row, home_team, 'L', True)
            updateForm(row, away_team, 'W', False)
        elif (result == 1):
            updateForm(row, home_team, 'D', True)
            updateForm(row, away_team, 'D', False)
        else:
            updateForm(row, home_team, 'W', True)
            updateForm(row, away_team, 'L', False)

    count += 1.0

home_form_points_df = pd.DataFrame(home_form_points_column)
home_form_GF_df = pd.DataFrame(home_form_GF_column)
home_form_GA_df = pd.DataFrame(home_form_GA_column)
home_form_GD_df = pd.DataFrame(home_form_GD_column)

away_form_points_df = pd.DataFrame(away_form_points_column)
away_form_GF_df = pd.DataFrame(away_form_GF_column)
away_form_GA_df = pd.DataFrame(away_form_GA_column)
away_form_GD_df = pd.DataFrame(away_form_GD_column)

fixture_data['home_form_points'] = home_form_points_df
fixture_data['home_form_GF'] = home_form_GF_df
fixture_data['home_form_GA'] = home_form_GA_df
fixture_data['home_form_GD'] = home_form_GD_df

fixture_data['away_form_points'] = away_form_points_df
fixture_data['away_form_GF'] = away_form_GF_df
fixture_data['away_form_GA'] = away_form_GA_df
fixture_data['away_form_GD'] = away_form_GD_df

fixture_data['form_points_dif'] = form_points_dif
fixture_data['form_GF_dif'] = form_GF_dif
fixture_data['form_GA_dif'] = form_GA_dif
fixture_data['form_GD_dif'] = form_GD_dif

fixture_data.to_csv(output_path, index=False)