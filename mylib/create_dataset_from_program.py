import re
import os
from glob import glob
import pandas as pd
import lhafile
import numpy as np
import mojimoji
import pickle

#######################################################################
## 番組表からデータフレームを作成
#-  [番組表](https://www1.mbrace.or.jp/od2/B/dindex.html)からDLした.lzhファイルを解凍
#- 解凍して.txt形式で保存する際に，DataFrameにしてデータ抽出
#- 複数ファイルのDataFrameをマージ
#######################################################################


def Make_df_RaceList(file_path, lzh_file_name):
    """
    lzh形式で圧縮された番組表ファイルから必要なデータを抽出してデータフレームに格納

    Parameters
    ----------
    file_path : _type_
        _description_
    lzh_file_name : _type_
        _description_
    """    
  
    #テキストファイルを読み込む
    with open(file_path, encoding='shift-jis') as f:
        data = f.readlines()
        #出走表を取り出す
    racers = [row.replace('\u3000','').replace('\n','') for row in data if re.match('^[1-6]\s', row)]

    #必要な13種類のデータを取り出す
    pattern = '^([1-6])\s(\d{4})([^0-9]+)(\d{2})([^0-9]+)(\d{2})([AB]\d{1})\s(\d{1}.\d{2})\s*(\d+.\d{2})\s(\d{1}.\d{2})\s*(\d+.\d{2})\s+\d+\s+(\d+.\d{2})\s*\d+\s+(\d+.\d{2})'

    # 上記のパターンを"pattern_re"として登録して使用する
    pattern_re = re.compile(pattern)
    try:
        values = [re.match(pattern_re, racer).groups() for racer in racers]
        #取り出したデータをデータフレームに入れる
        column = ['艇番', '選手登番', '選手名', '年齢', '支部', '体重', '級別', '全国勝率', '全国2連率', '当地勝率', '当地2連率', 'モーター2連率', 'ボート2連率']
        df_RaceList = pd.DataFrame(values,columns=column)

        # dr_RaceListに"レースID"列を追加する    
        df_RaceList["レースID"], df_RaceList["会場"] = get_Race_ID(df_RaceList, lzh_file_name, data)
    except:
        print("'NoneType' object has no attribute 'groups'発生，この処理はスキップします．")
        print("エラーファイル名 : ", lzh_file_name)
        values = []
        df_RaceList = pd.DataFrame()    


    return(df_RaceList)


def get_Race_ID(df, lzh_file_name, data):


    date = int(get_date(lzh_file_name)) # 日付
    race_count = len(get_race_count(data)) # 合計レース数
    place_ID =len(get_race_place_ID(data)) # 合計会場数
    racers_num = len(df.index) # レース出場者数の合計   


    race_count_list = [int(s) for s in get_race_count(data)] # 第何レースかのリスト（int変換）
    place_count_list = [int(s) for s in get_race_place_ID(data)] #会場のリスト(int変換) 

    print(lzh_file_name)
    print("1ファイル中のレース情報")
    print("--------------------------")
    print("出場者数 : ", racers_num)
    print("レース数 : ", race_count )
    print("会場数 : ", place_ID)
    print("--------------------------")
    race_rep_num = int(racers_num/race_count) # 合計レース数リストの複製数
    print("レース数繰り返し回数 : ", race_rep_num)
    place_rep_num = racers_num/place_ID # 合計会場数リストの複製数
    print("会場数繰り返し回数 : ", place_rep_num)
    print("--------------------------")
    #print("会場名リスト:" ,get_race_place_ID(data))
    # 一度文字列リストを数値のリストに変換し，numpyのメソッドで繰り返し生成したのち，文字列リストに再変換
    race_num = [str(s) for s in np.repeat(race_count_list, race_rep_num)]
    place_num = [str(s) for s in np.repeat(place_count_list, place_rep_num)]
    date_num = [str(s) for s in np.repeat(date, racers_num)]    

    Place_ID = place_num

    Race_ID = []
    for iii in range(racers_num):
        Race_ID.append(date_num[iii] + place_num[iii].zfill(2) + race_num[iii].zfill(2))  
        

    return(Race_ID, Place_ID)

def get_race_place(data : list ) -> list:
    '''
    会場名だけ記載され，結果の情報がない場合がある．
    その場合は，出場者数と会場数との関係に不整合が生じるため，該当する会場名は除外しておく．
    '''
    # 会場の抽出
    place = [row.replace('\u3000','').replace('\n','') for row in data if re.match('^[ボートレース]', row)]
    place = [row.replace("ボートレース", "") for row in place]
    place_name = []
    for iii in range(len(place)):
        a = re.findall(" .*", place[iii])
        if a == []:
            pass#place_name.append(place[iii])
        else:
            place_name.append(place[iii].replace(a[0], ""))
    return(place_name)

def get_race_place_ID(data : list ) -> list:
    '''
    会場名から会場コードを取得

    Return

    '''

    # 会場コードを辞書として登録しておく
    CircuitCode = {"桐生" : "01", "戸田" : "02", "江戸川" : "03", "平和島" : "04", "多摩川" : "05", "浜名湖" : "06", "蒲郡" : "07", "常滑" :  "08", "津" : "09", "三国" : "10", "びわこ" : "11", "住之江" : "12", "尼崎" : "13", "鳴門" : "14", "丸亀" : "15", "児島" : "16", "宮島" : "17", "徳山" : "18", "下関" : "19", "若松" : "20", "芦屋" : "21", "福岡" : "22", "唐津" : "23", "大村" : "24"}
    
    # 会場名の抽出
    place = get_race_place(data)
       

    # 登録コードと合致する会場を取得
    ID_search = []
    for iii in range(len(place)):
        ID_search.append(CircuitCode.get(place[iii]))   
    return(ID_search)


#print(get_race_place_ID(data))

def get_race_count(data : list) -> list:
    '''
    第何レースかを取得する．不要な文字列を削除し，全角数字を半角に変換．
    '''
    
    # 第何レースかの抽出
    race_num = [row.replace('\u3000','').replace('\n','') for row in data if re.search('.*?[０-９]Ｒ', row)]
    #race_num = [row.replace('\u3000','').replace('\n','') for row in data if re.search('Ｒ', row)]
    #print(race_num)
    race_num = [row[:3].replace(" ", "").replace("Ｒ","") for row in race_num] # 全角Rの削除，全角→半角変換
    #print(race_num)
    
    race_count = []
    for iii in range(len(race_num)):
        race_count.append(mojimoji.zen_to_han(race_num[iii]))
    #print(race_count)
    return(race_count)

#print(get_race_count(data))

def get_date(lzh_file_name):
    date = re.search("[0-9]{6}", lzh_file_name).group() #group()でマッチしたre.Machオブジェクトを文字列として取得
    return(date) 
#print(get_date(lzh_file_name))


if __name__ == "__main__":

    df_RaceList = pd.DataFrame()
    arr = []

    Base_dir = r'C:\Users\1te11\Dropbox\Obsidian4Cloud\004_Python\004_BoatRace\009_DataSets'
    os.chdir(Base_dir)

    # ダウンロードしたLZHファイルが保存されている場所を指定
    LZH_FILE_DIR = Base_dir + r'\program_lzh'
    os.chdir(LZH_FILE_DIR)
    # 解凍したファイルを保存する場所を指定
    TXT_FILE_DIR = Base_dir + r'\program_txt'

    # ファイルを格納するフォルダを作成
    os.makedirs(TXT_FILE_DIR, exist_ok=True)


    current_dir = os.getcwd()
    print("現在の作業ディレクトリ:", current_dir)

    # LZHファイルのリストを取得
    lzh_file_list = os.listdir(LZH_FILE_DIR)
    #print(lzh_file_list)


    # ファイルの数だけ処理を繰り返す
    for lzh_file_name in lzh_file_list:

        # 拡張子が lzh のファイルに対してのみ実行
        if re.search(".lzh", lzh_file_name):
            print(lzh_file_name, "を解凍中...")

            file = lhafile.Lhafile(LZH_FILE_DIR + "\\" + lzh_file_name)

            # 解凍したファイルの名前を取得
            info = file.infolist()
            name = info[0].filename

                   # 解凍したファイルの保存
            open(TXT_FILE_DIR + "\\" + name, "wb").write(file.read(name))

            df = Make_df_RaceList(TXT_FILE_DIR + "\\" + name, lzh_file_name)
            arr.append(df)      

            print(TXT_FILE_DIR + lzh_file_name + " を解凍してデータフレームへのマージが完了しました.")
            print("--------------------------------------")
    df_RaceList = pd.concat(arr, ignore_index = True)

    # 終了合図
    os.chdir(Base_dir)
    print("作業を終了しました")

    f = open('df_RaceList.pkl','wb')
    pickle.dump(df_RaceList,f)
    f.close  