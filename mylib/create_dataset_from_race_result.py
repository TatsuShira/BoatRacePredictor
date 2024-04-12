import re
import os
from glob import glob
import pandas as pd
import lhafile
import numpy as np
import mojimoji
import pickle


def Make_df_RaceList_Result(file_path, lzh_file_name):
  
    #テキストファイルを読み込む
    with open(file_path, encoding='shift-jis') as f:
        data = f.readlines()
        #出走表を取り出す
    ###########################
    #    順位等の抽出
    ###########################
    racers = [row.replace('\u3000','').replace('\n','') for row in data if re.match('^\s\s[a-zA-Z0-9_]{1,2}\s', row)]
    #必要なデータを取り出す
    # 展示タイムまでをパターンマッチングで抽出
    pattern = '^\s\s([a-zA-Z0-9_]{1,2}).*(\d{4}).*?([^0-9]+)\s.*?\d{1,2}.*?\d{1,3}.*?(\w.{,3}).*'

    # 上記のパターンを"pattern_re"として登録して使用する
    pattern_re = re.compile(pattern)
    values = [list(re.match(pattern_re, racer).groups()) for racer in racers]
    #print(len(values)/6)
    ###########################
    #    天候情報の抽出
    ###########################
    weathers = [row.replace('\u3000','').replace('\n','') for row in data if re.search('^\s.*?R', row)]
    weathers = [row for row in weathers if re.search('cm$', row)] # 末尾が"cm"で終わる行だけに絞り込み
    #必要なデータを取り出す
    # 展示タイムまでをパターンマッチングで抽出
    pattern_weathers = '^\s*(\d{1,2}).+H\d{1,4}m\s\s(\D{1,2}).+風\s\s(\D{1,2}).+(\d{1,2})m.+(\d{1,2})cm'

    # 上記のパターンを"pattern_re"として登録して使用する
    pattern_re_weathers = re.compile(pattern_weathers)
    values_weathers = [list(re.match(pattern_weathers, weather).groups()) for weather in weathers]

    a = [[]]
    try:

        for iii in range(len(values_weathers)):
            a.extend([values_weathers[iii]]*6)
        del a[0]
        values_weathers = a
        ###########################
        #    2つのリストを結合
        ###########################
        for i  in range(len(values_weathers)):
            values[i] += values_weathers[i] 

        #取り出したデータをデータフレームに入れる   
        column = ['着順', '選手登番', '選手名', '展示タイム', 'レース番号', '天候', '風向', '風量(m)', '波(cm)']
        df_RaceList_Result = pd.DataFrame(values,columns=column)  
        print(df_RaceList_Result.head())
        print("行数:", len(df_RaceList_Result))

        # dr_RaceListに"レースID"列を追加する    
        #get_race_place_result(data)
        df_RaceList_Result["レースID"] = get_Race_ID_result(df_RaceList_Result, lzh_file_name, data,values_weathers)  

        # 着順が数値以外のデータ行を削除
        df_RaceList_Result = df_RaceList_Result[(df_RaceList_Result["着順"] == "01") | (df_RaceList_Result["着順"] == "02") |(df_RaceList_Result["着順"] == "03") |(df_RaceList_Result["着順"] == "04") |(df_RaceList_Result["着順"] == "05") |(df_RaceList_Result["着順"] == "06")]


    except:
        print("list index out of rangeエラー発生，この処理はスキップします．")
        print("エラーファイル名: ",lzh_file_name)
        df_RaceList_Result = pd.DataFrame()
    
    

    return(df_RaceList_Result)
#TXT_FILE_DIR = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets\K221101.TXT'

def get_race_place_result(data : list ) -> list:
    '''
    会場名だけ記載され，結果の情報がない場合がある．
    その場合は，出場者数と会場数との関係に不整合が生じるため，該当する会場名は除外しておく．
    '''
    # 会場の抽出
  
    place = [row.replace('\u3000','').replace('\n','') for row in data if re.match('^.*［成績］', row)]
    #print(place)
    place = [row.replace("［成績］", "") for row in place]
    #print(place)
    place_name = []
    for iii in range(len(place)):
        a = re.findall(" .*", place[iii])
        if a == []:
            pass#place_name.append(place[iii])
        else:
            place_name.append(place[iii].replace(a[0], ""))
    print(place_name)
    return(place_name)
def get_race_place_ID_result(data : list ) -> list:
    '''
    会場名から会場コードを取得

    Return

    '''

    # 会場コードを辞書として登録しておく
    CircuitCode = {"桐生" : "01", "戸田" : "02", "江戸川" : "03", "平和島" : "04", "多摩川" : "05", "浜名湖" : "06", "蒲郡" : "07", "常滑" :  "08", "津" : "09", "三国" : "10", "びわこ" : "11", "住之江" : "12", "尼崎" : "13", "鳴門" : "14", "丸亀" : "15", "児島" : "16", "宮島" : "17", "徳山" : "18", "下関" : "19", "若松" : "20", "芦屋" : "21", "福岡" : "22", "唐津" : "23", "大村" : "24"}
    
    # 会場名の抽出
    place = get_race_place_result(data)
       

    # 登録コードと合致する会場を取得
    ID_search = []
    for iii in range(len(place)):
        ID_search.append(CircuitCode.get(place[iii]))   
    return(ID_search)
def get_date(lzh_file_name):
    date = re.search("[0-9]{6}", lzh_file_name).group() #group()でマッチしたre.Machオブジェクトを文字列として取得
    return(date) 
def get_Race_ID_result(df, lzh_file_name, data, values_weathers):


    date = int(get_date(lzh_file_name)) # 日付
    race_count = len(values_weathers) # 合計レース数
    place_ID =len(get_race_place_ID_result(data)) # 合計会場数
    racers_num = len(df.index) # レース出場者数の合計   


    #race_count_list = [int(s) for s in values_weathers] # 第何レースかのリスト（int変換）
    place_count_list = [int(s) for s in get_race_place_ID_result(data)] #会場のリスト(int変換) 


    print("1ファイル中のレース情報")
    print("--------------------------")
    print("出場者数 : ", racers_num)
    print("レース数 : ", race_count/6 )
    print("会場数 : ", place_ID)
    print("--------------------------")
    race_rep_num = int(racers_num/race_count) # 合計レース数リストの複製数
    print("レース数繰り返し回数 : ", race_rep_num)
    place_rep_num = racers_num/place_ID # 合計会場数リストの複製数
    print("会場数繰り返し回数 : ", place_rep_num)
    print("--------------------------")
    #print("会場名リスト:" ,get_race_place_ID(data))
    # 一度文字列リストを数値のリストに変換し，numpyのメソッドで繰り返し生成したのち，文字列リストに再変換
    #race_num = [str(s) for s in np.repeat(race_count_list, race_rep_num)]
    race_num = df["レース番号"]
    place_num = [str(s) for s in np.repeat(place_count_list, place_rep_num)]
    date_num = [str(s) for s in np.repeat(date, racers_num)]    

    Race_ID = []
    for iii in range(racers_num):
        Race_ID.append(date_num[iii] + place_num[iii].zfill(2) + race_num[iii].zfill(2))  

    return(Race_ID)

#df = Make_df_RaceList_Result(TXT_FILE_DIR, lzh_file_name)
def get_date(lzh_file_name):
    date = re.search("[0-9]{6}", lzh_file_name).group() #group()でマッチしたre.Machオブジェクトを文字列として取得
    return(date) 



if __name__ == "__main__":

    df_RaceList_Result = pd.DataFrame()
    arr = []

    Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets'
    os.chdir(Base_dir)

    # ダウンロードしたLZHファイルが保存されている場所を指定
    LZH_FILE_DIR = Base_dir + r'\result_lzh'
    os.chdir(LZH_FILE_DIR)
    # 解凍したファイルを保存する場所を指定
    TXT_FILE_DIR = Base_dir + r'\result_txt'

    # ファイルを格納するフォルダを作成
    os.makedirs(TXT_FILE_DIR, exist_ok=True)


    current_dir = os.getcwd()
    print("現在の作業ディレクトリ:", current_dir)

    # LZHファイルのリストを取得
    lzh_file_list = os.listdir(LZH_FILE_DIR)


    # ファイルの数だけ処理を繰り返す
    for lzh_file_name in lzh_file_list:

        # 拡張子が lzh のファイルに対してのみ実行
        if re.search(".lzh", lzh_file_name):

            file = lhafile.Lhafile(LZH_FILE_DIR + "\\" + lzh_file_name)

            # 解凍したファイルの名前を取得
            info = file.infolist()
            name = info[0].filename

                   # 解凍したファイルの保存
            open(TXT_FILE_DIR + "\\" + name, "wb").write(file.read(name))

            df = Make_df_RaceList_Result(TXT_FILE_DIR + "\\" + name, lzh_file_name)
            arr.append(df)      

            print(TXT_FILE_DIR + lzh_file_name + " を解凍しました")
    df_RaceList_Result = pd.concat(arr, ignore_index = True)

    # 終了合図
    os.chdir(Base_dir)
    print("作業を終了しました")

    f = open('df_RaceList_Result.pkl','wb')
    pickle.dump(df_RaceList_Result,f)
    f.close
       
