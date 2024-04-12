import sys, os
import pickle
import pandas as pd
from pycaret.classification import *
from sklearn.preprocessing import LabelEncoder

class BoatRacePredictor:
    def __int__(self):
        self.model_path = ""
        self.model_name = "model3"

    def load_model(self, model_dir : str, model_name : str):
        """
        モデルをロードする関数

        Parameters
        ----------
        model_dir : str
            モデルが保存されているディレクトリのパス

        model_name : str
            モデルのファイル名

        Returns
        -------
        _type_
            ロードされたモデル
        """
        model_path = os.path.join(model_dir,model_name)
        loaded_model = load_model(model_path)
        return loaded_model

    def preprocess_input_dataset(self, df_input_dataset : pd.DataFrame):
        """
        inputデータセットを基に偏差計算などの前処理を行う関数

        Parameters
        ----------
        df_input_dataset : pd.DataFrame
            前処理を行うデータセット

        Returns
        -------
        pd.DataFrame
            前処理が完了したデータセット
        """
        df = df_input_dataset

        # ラベルエンコード
        list_LabelEncode = ["選手名", "支部"]
        for label in list_LabelEncode:
            le = LabelEncoder()
            le.fit(df[label])
            df[label] = le.transform(df[label])

        # map関数でのエンコード
        class_mapping = {"B2" : 1, "B1" : 2, "A2" : 3, "A1" : 4}
        df["級別"] = df["級別"].map(class_mapping)

        # 偏差計算
        #偏差値に変える列名をリストで宣言
        list_std = ['全国勝率','全国2連率','当地勝率','当地2連率','モーター2連率','ボート2連率']

        #偏差値に変えてdfに戻す
        for list in list_std:
            df_std = df[list].astype(float)
            win_mean=df_std.mean()
            win_std=df_std.std()
            if win_std==0: #もしdf_stdが同じ値だとwin_stdが0になってしまう
                df[list]=50.0
            else:
                df[list] = df_std.apply(lambda x : ((x - win_mean)*10/win_std+50))

        # float64だとメモリが足らなくなるためfloat32に変換
        # object型はintに変換
        for i in range(len(df.columns)):
            if df.iloc[:,i].dtype == "float64":
                df.iloc[:,i] = df.iloc[:,i].astype("float32")
            else:
                df.iloc[:,i] = df.iloc[:,i].astype("int64")

        return df

    def race_prediction(self, model, df_input_dataset : pd.DataFrame, race_id : str) -> pd.DataFrame:
        """
        pycaretにより学習が完了したモデルを読み込み，予測を実行する関数

        Parameters
        ----------
        model : _type_
            pycaretにより生成されたモデル

        df_input_dataset : pd.DataFrame
            偏差計算などの前処理が完了したデータを入力すること

        race_id : str
            日付，レース場No., 第何レースかを組み合わせたレースID

        Returns
        -------
        pd.DataFrame
            予測結果のデータフレーム
        """
        race_ID_list = df_input_dataset["レースID"].unique()
        sr_race_ID_list = pd.Series(race_ID_list)
        print(sr_race_ID_list)

        # レース一覧から，検索値に該当するIDだけをピックアップしてシリーズに格納
        pred_race_list = sr_race_ID_list[sr_race_ID_list == int(race_id)]

        print("検索するレースID: ", pred_race_list)

        pred_data = df_input_dataset.groupby("レースID").get_group(race_ID_list[pred_race_list.index[0]])

        predictions = predict_model(model, data = pred_data)
        print(predictions)

        return predictions



if __name__ == "__main__":

    #Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace'
    Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets'


    pred = BoatRacePredictor()


    # モデルにデータを入れて予測
    CircuitCode = {"桐生" : "01", "戸田" : "02", "江戸川" : "03", "平和島" : "04", "多摩川" : "05", "浜名湖" : "06", "蒲郡" : "07", "常滑" :  "08", "津" : "09", "三国" : "10", "びわこ" : "11", "住之江" : "12", "尼崎" : "13", "鳴門" : "14", "丸亀" : "15", "児島" : "16", "宮島" : "17", "徳山" : "18", "下関" : "19", "若松" : "20", "芦屋" : "21", "福岡" : "22", "唐津" : "23", "大村" : "24"}

    #race_ID_list = df["レースID"].unique()
    #sr_race_ID_list = pd.Series(race_ID_list)

    # 検索値
    date = "230505"
    place = "17"
    race_num = "06"

    # 入力された値を基にレースIDを作成
    race_id = date + place + race_num
    

    model = pred.load_model(Base_dir, "model3")


    sys.path.append(r"C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\mylib")

    df_RaceList_for_pred = pd.DataFrame()
    Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets'
    os.chdir(Base_dir)

    df_RaceList_for_pred_dir = Base_dir + r'\df_RaceList_for_pred.pkl'
    with open(df_RaceList_for_pred_dir, 'rb') as p:
        df_RaceList_for_pred = pickle.load(p)

    df_RaceList_for_pred.head()
    df = df_RaceList_for_pred
    #print(df)

    preprocessed_df = pred.preprocess_input_dataset(df)
    #print(preprocessed_df)

    prediction =pred.race_prediction(model, preprocessed_df, race_id)
    #print(prediction)



