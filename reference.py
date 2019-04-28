import numpy as np
import pandas as pd
import warnings
import gc
import itertools
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss
from gatspy import datasets, periodic

warnings.simplefilter("ignore", DeprecationWarning)

data_path = "/modules/cs342/Assignment2/"
# prediction_column_names =
features = {
    'mjd': ["min", 'max', 'size'],
    'flux': ['min', 'max', 'mean', 'median', 'skew'],
    'flux_err': ['min', 'max', 'mean', 'median', 'std'],
    'detected': ['mean'],
    'flux_ratio_sq': ['sum', 'skew'],
    'flux_by_flux_ratio_sq': ['sum', 'skew'],
}

group_id = 'object_id'


def crossValidation(dataFrame, splits, tLabel, depth, estimators):
    df = dataFrame.copy()

    # Initialise kf with the given number of splits
    kf = KFold(n_splits=splits)
    bestModel = None
    logLoss = 0.0

    # For the training data and test data in each "split"/fold, we iterate through every alpha in the alphas
    # array passed into the method. So for eevery alpha in alphas for every fold/split we produce a model
    # using the training data, tLabel and given alpha
    for training, test in kf.split(df):
        trainingData = df.ix[training]
        training_y = trainingData['target']
        training_x = trainingData.drop('target', axis=1)

        testData = df.ix[test]
        validation_y = testData['target']
        validation_x = testData.drop('target', axis=1)

        model = RandomForestClassifier(n_estimators=estimators, max_depth=depth, random_state=0)
        model.fit(training_x, training_y)

        predictedValues = model.predict_proba(validation_x)
        log_result = log_loss(validation_y, predictedValues, labels=model.classes_)
        logLoss = logLoss + log_result

    del training_y
    del training_x
    del trainingData
    del validation_x
    del validation_y
    gc.collect()
    del df
    return logLoss / splits


def getBestHyperParameters(dataframe, splits, depth, estimators, tLabel):
    bestModelResult = [1000, 0, 0]
    curr_depth = 1

    while curr_depth <= depth:
        print("RUNNING AT DEPTH - " + str(curr_depth))

        result = crossValidation(dataframe, splits, tLabel, curr_depth, estimators)

        print(str(result) + "___" + str(bestModelResult[0]))

        if result < bestModelResult[0]:
            print("B E T T E R")
            bestModelResult = [result, curr_depth, estimators]

        curr_depth += 1

    return bestModelResult


def getFullTraining(training_grouped, meta_train):
    training_column_names = training_grouped.columns.tolist()
    meta_column_names = meta_train.columns.tolist()

    training_grouped_np = np.asarray(training_grouped)
    meta_np = np.asarray(meta_train)

    merged_np = np.column_stack((training_grouped_np, meta_np))

    full_training = pd.DataFrame(merged_np)
    full_training.columns = training_column_names + meta_column_names

    filler_value = full_training.mean(axis=0)
    full_training.fillna(filler_value, inplace=True)

    return full_training


def preprocessMeta(dataframe):
    del dataframe['object_id']
    del dataframe['distmod'], dataframe['hostgal_specz']
    del dataframe['ra'], dataframe['decl'], dataframe['gal_l'], dataframe['gal_b'], dataframe['ddf']

    return dataframe


def convertPassbandColumns(input, passband_number):
    result = []
    for entry in input:
        result.append(entry + "_" + str(passband_number))
    return result


def preprocess(training, meta_train):
    training['flux_ratio_sq'] = np.power(training['flux'] / training['flux_err'], 2.0)
    training['flux_by_flux_ratio_sq'] = training['flux'] * training['flux_ratio_sq']

    training_grouped = training.groupby(group_id).agg(features)
    new_columns_ = [
        k + '_' + agg for k in features.keys() for agg in features[k]
    ]
    training_grouped.columns = new_columns_

    training_grouped['mjd_diff'] = training_grouped['mjd_max'] - training_grouped['mjd_min']
    training_grouped['flux_diff'] = training_grouped['flux_max'] - training_grouped['flux_min']
    training_grouped['flux_dif2'] = (training_grouped['flux_max'] - training_grouped['flux_min']) / training_grouped[
        'flux_mean']
    training_grouped['flux_w_mean'] = training_grouped['flux_by_flux_ratio_sq_sum'] / training_grouped[
        'flux_ratio_sq_sum']
    training_grouped['flux_dif3'] = (training_grouped['flux_max'] - training_grouped['flux_min']) / training_grouped[
        'flux_w_mean']

    gc.collect()
    #######################################################

    full_training = training_grouped.reset_index().merge(
        right=meta_train,
        how='outer',
        on='object_id'
    )

    full_training.to_csv("full_training_example.csv")

    del full_training['hostgal_specz'], full_training['distmod']
    del full_training['ra'], full_training['decl'], full_training['gal_l'], full_training['gal_b'], full_training['ddf']
    gc.collect()

    return full_training


def splitGalactic(full_training, forTraining):
    full_training_galactic = full_training[full_training['hostgal_photoz'] == 0]
    full_training_galactic.to_csv("main_galactic_check.csv")
    full_training_extragalactic = full_training[full_training['hostgal_photoz'] != 0]
    full_training_extragalactic.to_csv("main_extragalactic_check.csv")

    galactic_flag = False
    extragalactic_flag = False
    if full_training_galactic.empty:
        print
        "Galactic Flag Set!"
        galactic_flag = True
    if full_training_extragalactic.empty:
        print
        "Extragalactic Flag Set!"
        extragalactic_flag = True

    gc.collect()
    if forTraining:
        galactic_target = full_training_galactic['target']
        extragalactic_target = full_training_extragalactic['target']
        del full_training_galactic['target']
        del full_training_extragalactic['target']

    full_training_galactic_mean = full_training_galactic.mean(axis=0)
    full_training_galactic.fillna(full_training_galactic_mean, inplace=True)

    full_training_extragalactic_mean = full_training_extragalactic.mean(axis=0)
    full_training_extragalactic.fillna(full_training_extragalactic_mean, inplace=True)

    ss = StandardScaler()

    if not galactic_flag:
        full_training_galactic_ids = full_training_galactic['object_id']
        full_training_galactic_ids = full_training_galactic_ids.reset_index()
        full_training_galactic_columns = full_training_galactic.columns.tolist()
        del full_training_galactic['object_id']
        full_training_galactic = ss.fit_transform(full_training_galactic)
        full_training_galactic = pd.DataFrame(full_training_galactic)
        full_training_galactic.columns = full_training_galactic_columns
        full_training_galactic['object_id'] = full_training_galactic_ids
        del full_training_galactic_ids['index']

    if not extragalactic_flag:
        full_training_extragalactic_ids = full_training_extragalactic['object_id']
        full_training_extragalactic_ids = full_training_extragalactic_ids.reset_index()
        full_training_extragalactic_columns = full_training_extragalactic.columns.tolist()
        del full_training_extragalactic['object_id']
        full_training_extragalactic = pd.DataFrame(ss.fit_transform(full_training_extragalactic))
        full_training_extragalactic.columns = full_training_extragalactic_columns
        full_training_extragalactic['object_id'] = full_training_extragalactic_ids
        del full_training_extragalactic_ids['index']

    ##ALL FUNCTIONING CORRECTLY, CORRECT NUMBER OF ENTRIES PER CLASS

    if forTraining:
        galactic_target = galactic_target.reset_index()
        extragalactic_target = extragalactic_target.reset_index()

        del galactic_target['index']
        del extragalactic_target['index']
        full_training_galactic['target'] = galactic_target
        full_training_extragalactic['target'] = extragalactic_target

    print
    full_training_galactic
    return [full_training_galactic, full_training_extragalactic]


def main():
    gc.enable()
    training = pd.read_csv(data_path + 'training_set.csv')
    meta_train = pd.read_csv(data_path + 'training_set_metadata.csv')
    full_training = preprocess(training, meta_train)

    result = splitGalactic(full_training, True)
    full_training_galactic = result[0]
    full_training_extragalactic = result[1]

    print
    full_training_galactic
    del training
    del meta_train
    gc.collect()
    ############################################################
    # PREPROCESSING - COMPLETE
    ############################################################
    ############################################################
    # START OF TRAINING
    ############################################################
    splits = 10
    bestModelResult = [10000, 0, 0]
    depth = 20
    estimators = 1
    tLabel = "target"

    # del full_training_galactic['index']
    galactic_best_hyper_parameters = getBestHyperParameters(full_training_galactic, 6, depth, estimators, tLabel)
    extragalactic_best_hyper_parameters = getBestHyperParameters(full_training_extragalactic, 8, depth, estimators,
                                                                 tLabel)
    gc.collect()
    # WHAT ARE SIZES OF THESE GALACTIC AND EXTRAGALACTIC CLASSES?

    galactic_logloss = galactic_best_hyper_parameters[0]
    galactic_best_depth = galactic_best_hyper_parameters[1]
    galactic_best_estimators = galactic_best_hyper_parameters[2]
    print("BEST MODEL - " + str(galactic_logloss) + "__" + str(galactic_best_depth))

    extragalactic_logloss = extragalactic_best_hyper_parameters[0]
    extragalactic_best_depth = extragalactic_best_hyper_parameters[1]
    extragalactic_best_estimators = extragalactic_best_hyper_parameters[2]
    print("BEST MODEL - " + str(extragalactic_logloss) + "__" + str(extragalactic_best_depth))

    # target = full_training['target']
    # del full_training['target']
    gc.collect()

    # best_model_produced = trainData(full_training, target, best_estimators, best_depth)

    galactic_best_model_produced = RandomForestClassifier(n_estimators=galactic_best_estimators,
                                                          max_depth=galactic_best_depth, random_state=0)
    galactic_targets = full_training_galactic['target']
    del full_training_galactic['target']
    gc.collect()
    galactic_best_model_produced.fit(full_training_galactic, galactic_targets)

    extragalactic_best_model_produced = RandomForestClassifier(n_estimators=extragalactic_best_estimators,
                                                               max_depth=extragalactic_best_depth, random_state=0)
    extragalactic_targets = full_training_extragalactic['target']
    del full_training_extragalactic['target']
    gc.collect()
    extragalactic_best_model_produced.fit(full_training_extragalactic, extragalactic_targets)

    extragal_column_names = full_training_galactic.columns.tolist()
    gal_column_names = full_training_galactic.columns.tolist()
    extragal_column_names = full_training_extragalactic.columns.tolist()
    del full_training_galactic
    del full_training_extragalactic
    del galactic_targets
    del extragalactic_targets
    gc.collect()

    feature_importance_headers = []
    for index, importance in enumerate(galactic_best_model_produced.feature_importances_):
        feature_importance_headers.append([gal_column_names[index], importance])

    print
    "FEATURE IMPORTANCES \n "
    for entry in feature_importance_headers:
        print
        "FEATURE: " + str(entry[0]) + "____IMPORTANCE: " + str(entry[1])
    print
    "SPLIT"
    feature_importance_headers = []
    for index, importance in enumerate(extragalactic_best_model_produced.feature_importances_):
        feature_importance_headers.append([extragal_column_names[index], importance])
    for entry in feature_importance_headers:
        print
        "FEATURE: " + str(entry[0]) + "____IMPORTANCE: " + str(entry[1])

    del gal_column_names
    del extragal_column_names
    gc.collect()

    ############################################################
    # END OF TRAINING
    ############################################################
    ############################################################
    # START OF TEST PREPROCESSING
    ############################################################
    test_data = pd.read_csv(data_path + 'training_set.csv', chunksize=40000)
    print
    "read test data in!"
    test_meta_data = pd.read_csv(data_path + 'training_set_metadata.csv')
    del test_meta_data['target']
    # del test_meta_data['target']
    print
    "read in the meta!"
    gc.collect()

    last_test_chunk = 0
    meta_start_pointer = 0
    meta_end_pointer = 0
    ratio_count = 0
    considerRemoved = False
    writeCount = 0
    progress = 0
    removed_data = 0
    checkCounter = 0
    removed_data = 0
    meta_chunk = 0
    for test_chunk in test_data:
        last_test_chunk = test_chunk.copy()
        test_chunk_ids = test_chunk['object_id'].unique()
        length = len(test_chunk_ids) - 1
        removed_ID = test_chunk_ids[length]
        if considerRemoved:
            print
            "CONSIDERING THE REMOVED ITEM BEFOREHAND"
            # consider previously removed values and append to the top of dataframe
            test_chunk = pd.concat([removed_data, test_chunk], ignore_index=True)
        else:
            considerRemoved = True
        removed_data = test_chunk[test_chunk['object_id'] == removed_ID]
        test_chunk = test_chunk[test_chunk['object_id'] != removed_ID]

        meta_end_pointer += length
        meta_chunk = test_meta_data.iloc[meta_start_pointer:meta_end_pointer]
        meta_start_pointer += length

        ratio = len(meta_chunk) / 3492890.0

        full_training = preprocess(test_chunk, meta_chunk)
        result = splitGalactic(full_training, False)
        full_training_galactic = result[0]
        full_training_extragalactic = result[1]

        galacticFlag = False
        extragalacticFlag = False
        if full_training_galactic.empty:
            galactic_flag = True
        if full_training_extragalactic.empty:
            extragalactic_flag = True

        print
        full_training_galactic

        progress += ratio_count * ratio
        print
        ""
        print
        ""
        print
        "CURRENTLY " + str(progress) + "% c  COMPLETE"
        print
        ""
        print
        ""
        ratio_count += 1

        ##########################################################
        # END OF TEST PREPROCESSING
        ##########################################################
        ##########################################################
        # START OF PREDICTION PHASE
        ##########################################################

        gal_result_column_names = galactic_best_model_produced.classes_
        extragal_result_column_names = extragalactic_best_model_produced.classes_

        gal_class_ids = []
        extragal_class_ids = []
        for identifier in gal_result_column_names:
            class_number = int(identifier)
            class_id = 'class_' + str(class_number)
            gal_class_ids.append(class_id)
        gal_class_ids.append('class_99')

        for identifier in extragal_result_column_names:
            class_number = int(identifier)
            class_id = 'class_' + str(class_number)
            extragal_class_ids.append(class_id)

        class_ids = gal_class_ids + extragal_class_ids

        if not galacticFlag:
            predictions = galactic_best_model_produced.predict_proba(full_training_galactic)
            length = len(predictions)
            zeros = np.full((length, len(extragal_class_ids) + 1), 0)

            galactic_ids = full_training_galactic['object_id']

            predictions = np.column_stack((predictions, zeros))
            # print predictions.shape
            # print galactic_object_ids
            predictions = np.column_stack((galactic_ids, predictions))
            predictions_df = pd.DataFrame(predictions)

            new_columns = ['object_id'] + class_ids
            predictions_df.columns = new_columns
            predictions_df['object_id'] = predictions_df['object_id'].apply(np.int64)
            # print predictions_df

            if writeCount == 0:
                predictions_df.to_csv('u1617935output.csv', mode='w', header=True, index=False)
                writeCount += 1
            else:
                predictions_df.to_csv('u1617935output.csv', mode='a', header=False, index=False)

        gc.collect()
        if not extragalacticFlag:
            predictions = extragalactic_best_model_produced.predict_proba(full_training_extragalactic)
            length = len(predictions)
            zeros = np.full((length, len(gal_class_ids)), 0)

            extragalactic_ids = full_training_extragalactic['object_id']

            predictions = np.column_stack((zeros, predictions))
            predictions = np.column_stack((extragalactic_ids, predictions))
            predictions_df = pd.DataFrame(predictions)

            new_columns = ['object_id'] + class_ids
            predictions_df.columns = new_columns
            predictions_df['object_id'] = predictions_df['object_id'].apply(np.int64)

            predictions_df.to_csv('u1617935output.csv', mode='a', header=False, index=False)
            gc.collect()

    max_length = test_meta_data.shape[0]
    print
    removed_data
    meta_single = test_meta_data.iloc[[max_length - 1]]
    meta_single = pd.DataFrame(meta_single)

    full_training_end = preprocess(removed_data, meta_single)
    result = splitGalactic(full_training_end, False)
    full_training_galactic_end = result[0]
    full_training_extragalactic_end = result[1]
    galactic_ids_end = full_training_galactic_end['object_id']
    extragalactic_ids_end = full_training_extragalactic_end['object_id']

    galacticFlag = False
    extragalacticFlag = False

    if full_training_galactic_end.empty:
        galacticFlag = True

    if full_training_extragalactic_end.empty:
        extragalacticFlag = True

    gal_result_column_names = galactic_best_model_produced.classes_
    extragal_result_column_names = extragalactic_best_model_produced.classes_

    gal_class_ids = []
    extragal_class_ids = []
    for identifier in gal_result_column_names:
        class_number = int(identifier)
        class_id = 'class_' + str(class_number)
        gal_class_ids.append(class_id)
    gal_class_ids.append('class_99')

    for identifier in extragal_result_column_names:
        class_number = int(identifier)
        class_id = 'class_' + str(class_number)
        extragal_class_ids.append(class_id)

    class_ids = gal_class_ids + extragal_class_ids

    print
    galacticFlag
    print
    extragalacticFlag

    if not galacticFlag:
        predictions = galactic_best_model_produced.predict_proba(full_training_galactic_end)
        length = len(predictions)
        zeros = np.full((length, len(extragal_class_ids) + 1), 0)

        predictions = np.column_stack((predictions, zeros))
        # print predictions.shape
        # print galactic_object_ids
        predictions = np.column_stack((galactic_ids_end, predictions))
        predictions_df = pd.DataFrame(predictions)

        new_columns = ['object_id'] + class_ids
        predictions_df.columns = new_columns
        predictions_df['object_id'] = predictions_df['object_id'].apply(np.int64)
        # print predictions_df

        print
        "output!!!"
        print
        predictions_df
        predictions_df.to_csv('u1617935output.csv', mode='a', header=False, index=False)
        gc.collect()

    gc.collect()
    if not extragalacticFlag:
        predictions = extragalactic_best_model_produced.predict_proba(full_training_extragalactic_end)
        length = len(predictions)
        zeros = np.full((length, len(gal_class_ids)), 0)

        predictions = np.column_stack((zeros, predictions))
        predictions = np.column_stack((extragalactic_ids_end, predictions))
        predictions_df = pd.DataFrame(predictions)

        new_columns = ['object_id'] + class_ids
        predictions_df.columns = new_columns
        predictions_df['object_id'] = predictions_df['object_id'].apply(np.int64)
        print
        "output!!!"
        print
        predictions_df
        predictions_df.to_csv('u1617935output.csv', mode='a', header=False, index=False)
        gc.collect()


main()
