# original class import
import webcam

# Standard imports
import matplotlib.pyplot as plt
import matplotlib as mpl
import cv2
import numpy as np
import glob
import pandas as pd
from tqdm import tqdm

# Scikit-learn imports
from sklearn.model_selection import train_test_split

# Keras/TensorFlow imports
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

plt.rcParams['font.family'] = 'Times New Roman' #全体のフォントを設定
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 22
plt.rcParams['axes.linewidth'] = 1.0# 軸の線幅edge linewidth。囲みの太さ
plt.rcParams['axes.grid'] = True
plt.rcParams['figure.subplot.left'] = 0.15
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.subplot.top'] = 0.95
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams["xtick.direction"] = "in"               #x軸の目盛線を内向きへ
plt.rcParams["ytick.direction"] = "in"               #y軸の目盛線を内向きへ
plt.rcParams["xtick.minor.visible"] = True           #x軸補助目盛りの追加
plt.rcParams["ytick.minor.visible"] = True           #y軸補助目盛りの追加
plt.rcParams["xtick.major.size"] = 10                #x軸主目盛り線の長さ
plt.rcParams["ytick.major.size"] = 10                #y軸主目盛り線の長さ
plt.rcParams["xtick.minor.size"] = 5                 #x軸補助目盛り線の長さ
plt.rcParams["ytick.minor.size"] = 5                 #y軸補助目盛り線の長さ

test_slice = slice( 0, 6 )     
img_threshold = 15

Na_pathlist = glob.glob("./data/22Na/*.tiff")
Na = webcam.AnalysisImage( Na_pathlist[test_slice], webcam.Na_slice )
Na.analyze(img_threshold)

Co_pathlist = glob.glob("./data/60Co/*.tiff")
Co = webcam.AnalysisImage( Co_pathlist[test_slice], webcam.Co_slice )
Co.analyze(img_threshold)

Sr_pathlist = glob.glob("./data/90Sr/*.tiff")
Sr = webcam.AnalysisImage( Sr_pathlist[test_slice], webcam.Sr_slice )
Sr.analyze(img_threshold)

Ba_pathlist = glob.glob("./data/133Ba/*.tiff")
Ba = webcam.AnalysisImage( Ba_pathlist[test_slice], webcam.Ba_slice )
Ba.analyze(img_threshold)

Eu_pathlist = glob.glob("./data/152Eu/*.tiff")
Eu = webcam.AnalysisImage( Eu_pathlist[test_slice], webcam.Eu_slice )
Eu.analyze(img_threshold)

Am_pathlist = glob.glob("./data/241Am/*.tiff")
Am = webcam.AnalysisImage( Am_pathlist[test_slice], webcam.Am_slice )
Am.analyze(img_threshold)

# Monazu_pathlist = glob.glob("./data/Monazu/*.tiff")
# Monazu = webcam.AnalysisImage( Monazu_pathlist[test_slice], webcam.Monazu_slice )
# Monazu.analyze(img_threshold)

# dataset1 = np.array([
#     Na.area,
#     Na.arc_len,
#     Na.luminance
# ]).T
# dataset1 = np.array([
#     Co.area,
#     Co.arc_len,
#     Co.luminance
# ]).T
dataset1 = np.array([
    Ba.area,
    Ba.arc_len,
    Ba.luminance
]).T
# dataset1 = np.array([
#     Eu.area,
#     Eu.arc_len,
#     Eu.luminance
# ]).T
dataset2 = np.array([
    Sr.area,
    Sr.arc_len,
    Sr.luminance
]).T
dataset3 = np.array([
    Am.area,
    Am.arc_len,
    Am.luminance
]).T

# ans1 = np.full_like( Na.area, 0 )
# ans1 = np.full_like( Co.area, 0 )
ans1 = np.full_like( Ba.area, 0 )
# ans1 = np.full_like( Eu.area, 0 )
ans2 = np.full_like( Sr.area, 1 )
ans3 = np.full_like( Am.area, 2 )

dataset = np.vstack([dataset1, dataset2, dataset3])
ans = np.hstack([ans1, ans2, ans3])

x_train, x_valid, t_train, t_valid = train_test_split(dataset, ans, test_size=0.3)

# モデルの定義
model = Sequential([
    Dense(units=10, activation='softsign', input_dim=3),  # ノード数が3の層を追加。活性化関数はシグモイド関数。
    Dense(units=10, activation='swish'),  # ノード数が3の層を追加。活性化関数はシグモイド関数。
    Dense(units=10, activation='swish'),  # ノード数が3の層を追加。活性化関数はシグモイド関数。
    # Dense(units=10, activation='swish'),  # ノード数が3の層を追加。活性化関数はシグモイド関数。
    # Dense(units=10, activation='softsign'),  # ノード数が3の層を追加。活性化関数はシグモイド関数。
    Dense(units=3, activation='softmax')  # ノード数が1の層を追加。活性化関数はシグモイド関数。
])

es = EarlyStopping(patience=100, verbose=0, mode='auto', restore_best_weights=True)
opt = Adam()
model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

#  トレーニング
history = model.fit(
    x=x_train,
    y=t_train,
    validation_data=(x_valid, t_valid),
    batch_size=1024,  # バッチサイズ。一回のステップで全てのデータを使うようにする。
    epochs=3000,  # 学習のステップ数
    verbose=0,  # 1とするとステップ毎に誤差関数の値などが表示される
    callbacks=es,  # ここでコールバックを指定します。
)

# モデルの保存
model.save(filepath='test_model.h5', save_format='h5')

print(len(dataset1), len(dataset2), len(dataset3))
print(len(x_train), len(x_valid))

result_batchnorm = pd.DataFrame(history.history)
# 目的関数の値
plt.figure(figsize=(8, 8))
result_batchnorm[['loss', 'val_loss']].plot()
plt.yscale("log")
plt.savefig("img/loss.png", dpi=600, transparent=True)
plt.show()
plt.figure(figsize=(8, 8))
result_batchnorm[['accuracy', 'val_accuracy']].plot()
plt.savefig("img/accuracy.png", dpi=600, transparent=True)
plt.show()