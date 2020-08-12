import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm_notebook as tqdm

def plot_history(data):
    epochs = len(data['val_loss'])
    val_accuracy = data['val_accuracy']
    val_loss = data['val_loss']
    accuracy = data['accuracy']
    loss = data['loss']
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 3.5))
    
    ax[0].plot(accuracy, label='Train Accuracy', linewidth=2, marker='x')
    ax[0].plot(val_accuracy, label='Validation Accuracy', linewidth=2, marker='o', linestyle='--')
    ax[1].plot(loss, label='Train Loss', linewidth=2, marker='x')
    ax[1].plot(val_loss, label='Validation Loss', linewidth=2, marker='o', linestyle='--')
    ax[0].grid()
    ax[1].grid()
    ax[0].legend()
    ax[1].legend()
    ax[0].set_title('Accuracy')
    ax[1].set_title('Loss')
    plt.show()
    
def plot_feature_importance(feature_names, feature_importance, number):
    fig, ax = plt.subplots(figsize=(6, int(number/3)))
    data = pd.DataFrame(np.array(list(zip(feature_names, feature_importance))), columns=['Feature', 'Importance'])
    data.Importance = data.Importance.astype(float)
    data = data.sort_values('Importance', ascending=False)
    data = data[:number]
    sns.barplot(data=data, x='Importance', y='Feature', palette='Blues', edgecolor='black', ax=ax)
    plt.show()
    
def label_encode_cols(data):
    encoders = []
    transformed_data = []
    for col in data.columns:
        encoder = LabelEncoder()
        encoded_data = pd.Series(encoder.fit_transform(data[col].astype(str)), name=col, index=data.index)
        encoders.append(encoder)
        transformed_data.append(encoded_data)
    encoders = dict(zip(mutation_cols, encoders))
    transformed_data = pd.concat(transformed_data, axis=1)
    return encoders, transformed_data

def data_interpolator(data):
    target_cols = data.loc[:, data.isna().any()].columns
    X = data[[x for x in data.columns if x not in target_cols]]
    targets = data[target_cols]
    X_numerical = X.select_dtypes(exclude=['object'])
    X_object = X.select_dtypes(include=['object'])
    if X_object.shape[0] > 0:
        X_object = pd.get_dummies(X_object)
    X = pd.concat([X_numerical, X_object], 1)
    dtc = DecisionTreeClassifier(max_depth=10, min_samples_leaf=10)
    for col in tqdm(target_cols):
        X_train, X_null, y_train = (X.loc[targets[col].notna(), :], 
                                    X.loc[targets[col].isna(), :], 
                                    targets[col].loc[targets[col].notna()])
        encoder = LabelEncoder()
        y_train = encoder.fit_transform(y_train)
        dtc.fit(X_train, y_train)
        y_null = encoder.inverse_transform(dtc.predict(X_null))
        data.loc[data[col].isna(), col] = y_null
    return data