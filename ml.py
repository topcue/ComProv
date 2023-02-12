from enum import unique
import os
import sys

import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,f1_score
from sklearn.metrics import RocCurveDisplay
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder

from util import *


# def manual_test(arch):
#   ds = load_dataset("dataset/dataset_{}.csv".format(arch))
#   ds = preprocess_ds(ds)
#   print("step0:", len(ds))

#   ##! filtering startup functions
#   for i, row in ds.iterrows():
#     if row.x1 <= 0.8 and row.optmz != 0:
#       ds = ds.drop(index=[i])
#     elif row.x1 > 0.8 and row.optmz == 0:
#       ds = ds.drop(index=[i])
#   print("step1:", len(ds))
  
#   ##! filtering inlined function
#   for i, row in ds.iterrows():
#     if row.x2 > 0.2 and row.optmz != 0:
#       ds = ds.drop(index=[i])
#   print("step2:", len(ds))


def preprocess_ds(ds):
  ##! 1) optmz o0 vs o1
  ##! phase2
  ds['optmz'] = ds['optmz'].apply(lambda x: 1 if x != 0 else 0)
  # ds['optmz'] = ds['optmz'].apply(lambda x: 1 if x != 1 else 0)

  ##! 2) encoding non-numeric features arch
  x = ds[["arch"]]
  new_col = ds["arch"].unique()

  oe = OrdinalEncoder()
  x = oe.fit_transform(x)
  ohe = OneHotEncoder()
  x = ohe.fit_transform(x).toarray()
  
  new_feature = pd.DataFrame(data = x, columns = new_col)
  new_ds = pd.concat([ds, new_feature],axis=1)
  new_ds.pop("arch")
  ds = new_ds

  #! 3) encoding compiler
  x = ds[["compiler"]]
  new_col = ds["compiler"].unique()

  oe = OrdinalEncoder()
  x = oe.fit_transform(x)
  ohe = OneHotEncoder()
  x = ohe.fit_transform(x).toarray()
  
  new_feature = pd.DataFrame(data = x, columns = new_col)
  new_ds = pd.concat([ds, new_feature],axis=1)
  # new_ds.pop("compiler")
  ds = new_ds

  #! 4) encoding with num of func 
  num_func = ds[["num_func"]]
  arr = []
  for num in num_func.values:
    if num[0] <= 10: arr.append(1)
    else: arr.append(0)

  new_feature = pd.DataFrame({"small":arr})
  new_ds = pd.concat([ds, new_feature],axis=1)
  ds = new_ds

  return ds


def split_dataset(x, y, train_size=0.5):
  train_x, test_x, train_y, test_y = \
    train_test_split(x, y, train_size=train_size, stratify=y)
  train_y = train_y.values.ravel()

  return train_x, test_x, train_y, test_y


def reg(train_x, test_x):
  scaler = StandardScaler()
  train_x = scaler.fit_transform(train_x)
  test_x = scaler.transform(test_x)
  return train_x, test_x


def get_colors(ds):
  colors = []
  patches = []
  num_func = ds.num_func
  compilers = ds.compiler
  file_names = ds.file_name

  #! nun_func
  # for n in num_func:
  #   if 0 < n and n <= 20: colors.append("red")
  #   elif 0 < 20 and n <= 30: colors.append("blue")
  #   else: colors.append("black")
  # patches.append(mpatches.Patch(color='red', label='(0, 20]'))
  # patches.append(mpatches.Patch(color='blue', label='(20, 30]'))
  # patches.append(mpatches.Patch(color='black', label='(30, max]'))

  #! compiler
  for file_name in file_names:
    if "gcc" in file_name: colors.append("red")
    else: colors.append("black")
  patches.append(mpatches.Patch(color='red', label="gcc"))
  patches.append(mpatches.Patch(color='black', label="clang"))

  #! none
  if not colors: colors = [ "black" for _ in range(len(num_func)) ]
  if not patches: patches = [mpatches.Patch(color='black')]

  return colors, patches


def display_plot(arch):
  ds = load_dataset("dataset/dataset_{}.csv".format(arch))

  ##! here
  # ds = ds[ds["compiler"].str.contains("clang")]
  # ds = ds[ds["compiler"].str.contains("gcc")]
  # ds = ds.drop(ds[ds["file_name"].str.contains("gcc-8")].index)

  colors, patches = get_colors(ds)
  plt.scatter(x=ds[["x1"]], y=ds[["optmz"]], s=1, c=colors, label=colors)
  plt.xlabel("feature")
  plt.ylabel("optmz level")
  # plt.yticks([0, 1, 2, 3, 4, 5])
  plt.yticks(np.arange(0, 6), ("o0", "o1", "o2", "o3", "os", "of"))

  plt.title(arch)
  plt.legend(handles=patches)
  
  # plt.show()
  plt.savefig("/home/topcue/Dropbox/graph.png", dpi=500)


def select_features(ds):
  ##! here
  # selected_features = ["x1", "x4"] ##! good arm32

  ds = ds[ds["compiler"].str.contains("gcc")]
  # ds = ds.drop(ds[ds["file_name"].str.contains("gawk")].index)

  selected_features = ["x1", "x2", "x4"]

  print("[*] selected features:", selected_features)
  x = ds[selected_features]
  y = ds[["optmz"]]

  return np.array(x), np.array(y).ravel()


def kfold(arch):
  ds = load_dataset("dataset/dataset_{}.csv".format(arch))
  ds = preprocess_ds(ds)
  x, y = select_features(ds)

  accuracy_history = []
  f1_score_history = []
  kf = StratifiedKFold(n_splits=9, shuffle=True)
  for train_index, test_index in kf.split(x, y):
    ##! flip
    train_index, test_index = test_index, train_index
    train_x, test_x = x[train_index], x[test_index]
    train_y, test_y = y[train_index], y[test_index]

    ##! reg
    train_x, test_x = reg(train_x, test_x)

    ##! select model
    # model = SVC(kernel='rbf', C=1, gamma=0.1)
    model = RandomForestClassifier(n_estimators=100)

    model.fit(train_x, train_y)
    y_pred = model.predict(test_x)
    accuracy_history.append(accuracy_score(y_pred, test_y))
    f1_score_history.append(f1_score(y_pred, test_y))

  for accuracy in accuracy_history:
    print("acc:", round(accuracy, 5))
  print("[*] accuracy mean:", round(np.mean(accuracy_history) * 100, 3))
  # print("[*] f1 score mean:", round(np.mean(f1_score_history) * 100, 2))


if __name__ == "__main__":
  if len(sys.argv) < 2: eprint("Arg Err")
  arch = sys.argv[1]
  
  # manual_test(arch)
  
  display_plot(arch)
  kfold(arch)

# EOF
