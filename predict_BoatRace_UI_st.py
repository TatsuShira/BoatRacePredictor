# 必要なモジュールをインポート
import os, sys
import pickle
import pandas as pd
from datetime import datetime
from mylib.pred_boat_race import BoatRacePredictor as br
import streamlit as st

# ページレイアウトを広げる
st.set_page_config(layout='wide')

# 会場名の辞書を作成
CircuitCode0 = {"桐生" : "01", "戸田" : "02", "江戸川" : "03", "平和島" : "04", "多摩川" : "05", "浜名湖" : "06", "蒲郡" : "07", "常滑" :  "08", "津" : "09", "三国" : "10", "びわこ" : "11", "住之江" : "12", "尼崎" : "13", "鳴門" : "14", "丸亀" : "15", "児島" : "16", "宮島" : "17", "徳山" : "18", "下関" : "19", "若松" : "20", "芦屋" : "21", "福岡" : "22", "唐津" : "23", "大村" : "24"}

Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace'

# モデルのロード
br = br()
model = br.load_model(Base_dir, "model3")

sys.path.append(r"C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\mylib")

df_RaceList_for_pred = pd.DataFrame()
Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets'
os.chdir(Base_dir)

df_RaceList_for_pred_dir = Base_dir + r'\df_RaceList_for_pred.pkl'
with open(df_RaceList_for_pred_dir, 'rb') as p:
    df_RaceList_for_pred = pickle.load(p)

df = df_RaceList_for_pred
preprocessed_df = br.preprocess_input_dataset(df)

# Streamlit UI
date = st.sidebar.date_input('日付を選択してください')
CircuitCode = st.sidebar.selectbox('会場名を選択してください', list(CircuitCode0.keys()))
race = st.sidebar.text_input('レース番号を入力してください')
# ボタンが押されたら予測実行
if st.sidebar.button('予測実行'):
    # 入力された値を基にレースIDを作成
    race_id = str(date.strftime("%y%m%d") + str(CircuitCode0[CircuitCode]) + str(race.zfill(2)))
    df = br.race_prediction(model, preprocessed_df, race_id) # 予測実行
    st.dataframe(df) # 予測結果を表示