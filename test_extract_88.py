# 88四国地整：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
import re


# inputfile = "02 入札説明書【令和5年度　山鳥坂ダム月野尾工事用道路工事】.txt"
# inputfile = "02-1 入札説明書【R5 早明浦ダム周辺環境整備工事】.txt"
# inputfile = "02-1入札説明書【R5 香川管内安全施設工事】.txt"
# inputfile = "1101_02 入札説明書【令和5年度　愛南地区舗装修繕工事】.txt"
# inputfile = "0601_01-1 入札説明書.txt"
# inputfile = "0711_02 入札説明書本文.txt"
inputfile = "【88】四国_1225修正02-1入札説明書【R6-7 善通寺管内防災対策工事】.txt"
# inputfile = "88_test_input.txt"


with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(inputfile)
print(len(text))
print("総合評価に関する評価項目" in text)

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本官工事の場合は「本官」）

if ("四国地方整備局" in text):
  name_bu ="四国地方整備局"

print(name_bu)

print(("支出負担行為担当官" in text) and ("四国地方整備局長" in text))  # 本官と分任官工事とのルーチン分け
if ("支出負担行為担当官四国地方整備局長" in text):  # 本官と分任官とのルーチン分け
  name_of = "本官"
else:  # 事務所名抽出：１つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("四国地方整備局")        # ”四国地方整備局”の前半をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("所長")                  # "所長"の文字列の前をタプルとして抽出
  text0 = t0[0]
  name_of = text0.strip() + "所"              # 冒頭空白文字を削除して、抽出した文字列に"所"を追加

print(name_of)

# 工事名の抽出
# name_co  工事名 
# (1) 工事名 , (2) 工事場所 で文字列を抽出スライス

t0 = text.partition("工事名")  # "工事名"の文字列の後をタプルとして抽出
text0 = t0[-1]
t0 = text0.partition("(2)")    # 次行にある(2)の文字列の前をタプルとして抽出
text0 = t0[0]
t0 = text0.partition("（電子入札及び電子契約対象案件）")  # "（電子入札対象案件）"文字列の前をタプルとして抽出
text0 = t0[0]
name_co =text0.strip()         # 前後の空白文字を削除

print(name_co)
doushu_co = ""
#　同種工事の要件文字列の抽出（企業） doushu_co

if ("下記の条件を満足する同種工事を施工した実績を有すること" in text) :  # 記載があるかの判定
  t0 = text.partition("下記の条件を満足する同種工事を施工した実績を有すること")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  if ("実績に限る。・同種工事として、" in text0):  # "・"以降の表記ゆれ対応
    t1 = text0.partition("実績に限る。・同種工事として、")   # 後の文字列をタプルとして抽出
  elif ("実績に限る。同種工事とは、" in text0): # "・"以降の表記ゆれ対応
    t1 = text0.partition("実績に限る。同種工事とは、")   # 後の文字列をタプルとして抽出
  else:
    t1 = text0.partition("実績に限る。・") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("なお、当該実績が") # 文字列の前をタプルとして抽出 
  text1 =t1[0]
  doushu_co = text1.replace("を有すること。","") # ”を有すること。”を空文字置換
elif ("下記の条件を満足する同種工事１を施工した実績を有すること" in text): 
  # 企業の実績を同種工事１としている記述への対応（本官工事）
  t0 = text.partition("下記の条件を満足する同種工事１を施工した実績を有すること")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  t1 = text0.partition("同種工事１とは、") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("なお、当該実績は") # 文字列の前をタプルとして抽出
  text1 = t1[0]
  doushu_co = text1.replace("を有すること。","") # ”を有すること。”を空文字置換

#　同種工事の要件文字列の抽出（技術者） doushu_en

print("confirm : " , text0 , "FINISH")

if name_of != "本官": # 分任官工事・本官工事とのサブルーチン分け
  if ("同種工事（上記（４）に掲げる工事）の経験を有する者であること" in text):  # 記載があるかの判定
    doushu_en = doushu_co 
  else:
    t1 = text0.partition("元請けの技術者として") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("（共同企業体の構成員としての経験は") # 文字列の前をタプルとして抽出
    text1 = t1[0]
    doushu_en = text1.replace("を有すること。", "")
elif ("同種工事２の経験を有する者" in text):
    # 技術者の実績を同種工事２としている記述への対応（本官工事）
    t1 = text0.partition("同種工事２とは") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("なお、当該経験は") # 文字列の前をタプルとして抽出
    text1 = t1[0]
    # print("confirm : " , text1)
    doushu_en = text1.replace("を有すること。", "")

print("「同種工事（企業）」", doushu_co)
print("「同種工事（技術者）」", doushu_en)


# より同種性の高い工事／同種性が認められる工事の内容の抽出
# （２）入札の評価に関する基準　の項目において
# 表外の記載からそれぞれの内容を抽出する
# doushusei_en[0] 技術者での「より高い同種性が認められる工事」の内容
# doushusei_en[1] 技術者での「同種性が認められる工事」の内容　≒同種工事
# doushusei_co[0] 企業での「より高い同種性の高い工事」の内容
# doushusei_co[1] 企業での「同種性が認められる工事」の内容　≒同種工事 
# score_en 技術者での同種工事の施工実績での配点点数 (str)　# 要検討：表内抽出
# score_co 企業での同種工事の施工実績での配点点数 (str)  　# 要検討：表内抽出

doushusei_co = list()
doushusei_en = list()

if name_of != "本官": # 本官以外の場合
  if (("「より同種性の高い工事」：" in text) or ("「同種性が認められる工事」" in text)):
    # 上記文字列で表外記載がある場合の処理ルーチン 
    t0 = text.partition("１）技術者評価") # "１）技術者評価"後の文字列をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("」における「より同種性の高い工事」とは、")  #"「より同種性の高い工事」とは、"の後の文字列をタプルとして抽出
    text1 = t1[-1]
    if ("を有することとする。" in text1):
      t1 =text1.partition("を有することとする。") # 表記揺れ対応
    else:
      t1 = text1.partition("とする。") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    doushusei_en.insert(0, text1) 
    t1 = text0.partition("「同種性が認められる工事」とは、") # 後の文字列を抽出
    text1 = t1[-1]
    if ("記載している同種工事を示す。" in text1):
      doushusei_en.insert(1, doushu_en)
    # 同種工事の施工経験・表内の配点文字列の抽出 （！！要改良！！リスト化！！）
    # t0 = text0.partition("技より同種性の高い") # 後の文字列をタプルとして抽出
    # text0 = t0[-1]
    # t1 = text0.partition("術者等工事") # 前の文字列をタプルとして抽出
    # text1 = t1[0]
    # score_en = text1
    # t1 = text0.partition("同種性が認められ") # 後の文字列をタプルとして抽出
    # text1 = t1[-1]
    # t1 = text1.partition("る工事担当技術者") # 前の文字列をタプルとして抽出
    # text1 = t1[0]
    # score_en = score_en + " " + text1
    # ！！要改良！！リスト化！！
    
    t0 = text0.partition("．企業の施工実績") # 後の文字列をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("示す。「より同種性の高い工事」とは、") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    if ("を有することとする。" in text1): # 表記ゆれ対応
      t1 = text1.partition("を有することとする。")
    else:  
      t1 = text1.partition("とする。") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    doushusei_co.insert(0, text1)
    t1 = text0.partition("「同種性が認められる工事」とは、")
    text1 = t1[-1]
    if ("記載している同種工事を示す。" in text1):
      doushusei_co.insert(1, doushu_co)
    # 同種工事の施工実績・表内の配点文字列の抽出 （！！要改良！！リスト化！！）
    # t1 = text0.partition("より同種性の高い工事の実績")
    # text1 = t1[-1]
    # t1 = text1.partition("／")
    # text1 = t1[0]
    # score_co = text1
    # t1 = text0.partition("同種性が認められる工事の実績")
    # text1 = t1[-1]
    # t1 = text1.partition("Ⅰ－ⅱ工事成績評定")
    # text1 = t1[0]
    # score_co = score_co + " " + text1
elif ("同種工事２の経験を有する者" in text):
  # 技術者の実績を同種工事２としている記述への対応（本官工事）
  t0 = text.partition("１）技術者評価")
  text0 = t0[-1]
  t1 = text0.partition("「より同種性の高い工事」とは、同種工事２のうち「")  # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("」とする。") # 前の文字列をタプルとして抽出
  text1 = t1[0]
  doushusei_en.insert(0, text1) 
  t1 = text0.partition("「同種性が認められる工事」とは、") # 後の文字列を抽出
  text1 = t1[-1]
  if ("記載している同種工事２を示す。" in text1):
    doushusei_en.insert(1, doushu_en)
  # 企業の実績を同種工事１としている記述への対応（本官工事）
  t0 = text0.partition("．企業の施工実績") # 後の文字列を抽出
  text0 = t0[-1]
  t1 = text0.partition("「より同種性の高い工事」とは、同種工事１のうち「")
  text1 = t1[-1]
  t1 = text1.partition("」とする。")
  text1 = t1[0]
  doushusei_co.insert(0, text1)
  t1 = text0.partition("「同種性が認められる工事」とは、")
  text1 = t1[-1]
  if ("記載している同種工事１を示す。" in text1):
    doushusei_co.insert(1, doushu_co)



print("「より同種性の高い（企業）」", doushusei_co[0])
print("「同種性が認められる（企業）」", doushusei_co[1])
# print("「同種性配点（企業）」", score_co)    
print("「より同種性の高い（技術者）」", doushusei_en[0])
print("「同種性が認められる（技術者）」", doushusei_en[1])
# print("「同種性配点（技術者）」", score_en)
