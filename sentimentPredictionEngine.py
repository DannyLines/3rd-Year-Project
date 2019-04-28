import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import PolynomialFeatures
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Training data contains:
# Current match score
# Goals for
# Goals Against
# Points in league
# Sentiment analysis

# TO DO
# Scrape goals for and against for all premier league clubs
# Scrape points for all teams
# BOTH of the above need to be automated scripts that update a csv that is run periodically
# https://www.premierleague.com/matchweek/3284/table

# Current match score is already scraped, need to figure out how to add this to predictions

# Sentiment analysis - Start with just an overall total of positive tweet % and negative %
# Then can expand out into more fine tuned measures


Team_abbreviations = {
    "liverpool": 5,
    "man city": 2,
    "tottenham": 3,
    "chelsea": 1,
    "arsenal": 4,
    "man utd": 6,
    "leicester": 7,
    "west ham": 8,
    "watford": 9,
    "wolves": 10,
    "everton": 11,
    "bournemouth": 12,
    "brighton": 13,
    "crystal palace": 14,
    "newcastle": 15,
    "burnley": 16,
    "cardiff city": 17,
    "southampton": 18,
    "fulham": 19,
    "huddersfield": 20,
    "Aston Villa": 21,
    "Wigan": 22,
    "Blackburn": 23,
    "Bolton": 24,
    "Sunderland": 25,
    "Portsmouth": 26,
    "Stoke": 27,
    "Hull": 28,
    "Birmingham": 29,
    "West Brom": 30,
    "Blackpool": 31,
    "QPR": 32,
    "Norwich": 33,
    "Swansea": 34,
    "reading": 35,
    "Middlesbrough": 36

}

def cross_validation(df, splits, depth, estimators, tLabel):
    target_data = df['FTR']
    fixture_data = df.copy()
    #fixture_data.drop(['FTR'], axis=1, inplace=True)

    kf = KFold(n_splits=splits)
    logLoss = 0

    for training, test in kf.split(fixture_data):
        data = fixture_data.ix[training]

        training_target = data[tLabel]
        training_data = data.drop(['FTR'], axis=1)

        test_data = fixture_data.ix[test]

        validation_data = test_data.drop(['FTR'], axis=1)
        validation_test = test_data[tLabel]

        model = RandomForestClassifier(n_estimators=estimators, max_depth=depth, random_state=0)
        model.fit(training_data, training_target)
        print(model.classes_)
        predicted_vals = model.predict_proba(validation_data)
        acc_result = log_loss(validation_test, predicted_vals, labels=model.classes_)

        logLoss += acc_result
    print(logLoss/splits)
    return logLoss / splits

def getBestHyperParamters(df, splits, max_depth, estimators, tLabel):
    bestModelResult = [1299, 0]
    current_depth = 1
    while current_depth <= max_depth:
        result = cross_validation(df, splits, current_depth, estimators, tLabel)
        print(current_depth)
        if(result < bestModelResult[0]):
            bestModelResult = [result, current_depth]

        current_depth += 1
    print("Result - " + str(bestModelResult[0]))
    return bestModelResult

def preprocess(df):
    new_df = df.copy()
    new_df['MFH_home_acc'] = (new_df['MFH_home_target'] / new_df['MFH_home_attempts'])
    new_df['MFH_home_acc'] = new_df['MFH_home_acc'].replace([np.inf, -np.inf], np.nan)
    new_df['MFH_home_acc'] = new_df['MFH_home_acc'].fillna(0)

    #new_df = new_df.drop(['home_form_points', 'home_form_GF', 'home_form_GA', 'home_form_GD', 'away_form_points', 'away_form_GF','away_form_GA', 'away_form_GD'],axis=1)

    new_df['MFH_away_acc'] = (new_df['MFH_away_target'] / new_df['MFH_away_attempts'])
    new_df['MFH_away_acc'] = new_df['MFH_away_acc'].replace([np.inf, -np.inf], np.nan)
    new_df['MFH_away_acc'] = new_df['MFH_away_acc'] = new_df['MFH_away_acc'].fillna(0)

    return new_df

def main():
    directory_path = "static/csv/"
    file_path = directory_path + "training_data.csv"
    fixture_data = pd.read_csv(file_path)

    fixture_data = fixture_data.sample(frac=1)

    #fixture_data.drop(['Date', 'Referee', 'HF', 'AF', 'HY', 'AY', 'HC', 'AC', 'FTHG', 'FTAG'], axis=1, inplace=True)
    #fixture_data.drop(['Date', 'Referee', 'HTHG', 'HTAG', 'HR', 'AR', 'HTR', 'HF', 'AF', 'HY', 'AY', 'HC', 'AC', 'FTHG', 'FTAG'], axis=1, inplace=True)
    #fixture_data['HTGD'] = fixture_data['HTHG'] - fixture_data['HTAG']
    #away_goals_figures = fixture_data['HTAG']
    results = fixture_data['FTR']

    colors = []
    for row in fixture_data['FTR']:
        if row == 0:
            colors.append("red")
        elif row == 1:
            colors.append("black")
        elif row == 2:
                colors.append("green")

    target_data = fixture_data['FTR']
    data = fixture_data.drop('FTR', axis=1)

    #Data should be:
        # Home Team, Away team, MFH_result, home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points,
        # MFH_home_sentiment, MFH_away_sentiment, MFH_home_goals, MFH_away_goals, MFH_home_pos, MFH_away_pos,
        # MFH_home_attempts, MFH_away_attempts, MFH_home_target, MFH_away_target

    data = data[['HomeTeam', 'AwayTeam', 'MFH_result', 'home_GF', 'home_GA', 'home_GD', 'home_points',
                                 'away_GF', 'away_GA', 'away_GD', 'away_points', 'MFH_home_sentiment', 'MFH_away_sentiment',
                                 'MFH_home_goals', 'MFH_away_goals', 'MFH_home_pos', 'MFH_away_pos', 'MFH_home_attempts',
                                 'MFH_away_attempts', 'MFH_home_target', 'MFH_away_target']]
    print(target_data)
    new_data_df = preprocess(data)
    new_data_df['FTR'] = target_data

    check_data = {
                    'col1': [1],
                    'col2': [2],
                    'col3': [0],
                    'col4': [1],
                    'col5': [1],
                    'col6': [12],
                    'col7': [15],
                    'col8': [4],
                    'col9': [9],
                    'col10': [0],
                    'col11': [0],
                    'col12': [0]
                }

    check = pd.DataFrame(check_data)
    estimators = 250
    splits = 3
    depth = 25
    tLabel = 'FTR'
    print("DATA CHECK")
    print(new_data_df.columns.tolist())
    print(new_data_df)

    best_model_params = getBestHyperParamters(new_data_df, splits, depth, estimators, tLabel)
    best_model = RandomForestClassifier(n_estimators=500, max_depth=best_model_params[1], random_state=0)

    print(new_data_df.columns.tolist())

    new_data_df = new_data_df.drop('FTR', axis=1)
    best_model.fit(new_data_df, target_data)

    filename = 'MFH_PredictionModel.sav'
    pickle.dump(best_model, open(filename, 'wb'))

    print(new_data_df.columns.tolist())
    result = best_model_params[0]

    #print(best_model.predict_proba(check))
    print("DEPTH - " + str(best_model_params[1]) + " ------ RESULT - " + str(result))

    column_names = new_data_df.columns.tolist()
    feature_importance_headers = []
    for index, importance in enumerate(best_model.feature_importances_):
        feature_importance_headers.append([column_names[index], importance])

    y_vals = []
    headers = []
    for entry in feature_importance_headers:
        y_vals.append(entry[1])
        headers.append(entry[0])

    print("FEATURE IMPORTANCES \n ")
    for entry in feature_importance_headers:
        print("FEATURE: " + str(entry[0]) + "____IMPORTANCE: " + str(entry[1]))

    N = len(feature_importance_headers)
    x = range(N)
    plt.bar(x, y_vals, align='center', alpha=0.75)
    plt.ylabel("Feature Importance")
    plt.xlabel("Features")
    plt.xticks(x, headers, rotation='vertical')
    plt.show()
main()