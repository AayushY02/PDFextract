# 87中国地整：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
import re


# inputfile = "230619-松江-01説明書.txt"
# inputfile = "【訂正230531】230526-鳥取-03説明書.txt"
# inputfile = "230613-広島国道ｰ02入札説明書.txt"
# inputfile = "230512-本官-01入札説明書.txt"
# inputfile = "230607-太田川-入札説明書.txt"
inputfile = "【87】中国_【修正】250114-広砂-01 入札説明書.txt"

with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(inputfile)
print(len(text))
print("総合評価に関する事項" in text)

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本官工事の場合は「本官」）

if ("中国地方整備局" in text):
  name_bu ="中国地方整備局"

print(name_bu)

print(("支出負担行為担当官" in text) and ("中国地方整備局長" in text))  # 本官と分任官工事とのルーチン分け
if ("支出負担行為担当官中国地方整備局長" in text):  # 本官と分任官とのルーチン分け
  name_of = "本官"
else:  # 事務所名抽出：１つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("中国地方整備局")        # ”中国地方整備局”の前半をタプルとして抽出
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
t0 = text0.partition("（電子入札対象案件）")  # "（電子入札対象案件）"文字列の前をタプルとして抽出
text0 = t0[0]
name_co =text0.strip()         # 前後の空白文字を削除

print(name_co)

#　同種工事の要件文字列の抽出（企業） doushu_co
if (("同種工事とは、" in text) and ("なお、同種工事の施工実績は、" in text)):  # 記載があるかの判定
  t0 = text.partition("同種工事とは、")   # "同種工事とは、"の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("なお、同種工事の施工実績は、") # 文字列の前をタプルとして抽出
  text0 =t0[0]
  doushu_co = text0.strip() # 前後の空白文字を削除

#　同種工事の要件文字列の抽出（技術者） doushu_en
if ("現場での作業に配置する技術者は、" in text):  # 記載があるかの判定
  t0 = text.partition("現場での作業に配置する技術者は、")  # "現場での作業に配置する技術者は、"の文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("同種工事とは、") # 文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("ただし、") # 文字列の前をタプルとして抽出
  text0 = t0[0]
  doushu_en = text0.strip() # 前後の空白文字を削除 
elif ("基準を満たす主任技術者又は監理技術者を当該工事に" in text):  # 記載があるかの判定
  t0 = text.partition("基準を満たす主任技術者又は監理技術者を当該工事に")  # 文字列の後をタプルとして抽出
  text0 = t0[-1]
  if (("に掲げる同種工事の経験を有する者であること。" in text0) or 
      ("の同種工事の施工実績を有していること。" in text0)): # 企業部分と同種工事の技術者実績の記載があるかの判定
    doushu_en = doushu_co
  
print("「同種工事（企業）」", doushu_co)
print("「同種工事（技術者）」", doushu_en)


# より同種性の高い／同種性の高い工事の内容の抽出
# 5. 技術的能力の審査及び総合評価に関する事項 において、
# 下記の表記が箇条書き表記で見られる場合は、リストに降順に入力
# doushusei_co[0] 企業での「より高い同種性が認められる工事」の内容
# doushusei_co[1] 企業での「高い同種性が認められる工事」の内容
# doushusei_co[2] 企業での「同種性が認められる工事」の内容
# doushusei_en[0] 技術者での「より高い同種性が認められる工事」の内容
# doushusei_en[1] 技術者での「高い同種性が認められる工事」の内容
# doushusei_en[2] 技術者での「同種性が認められる工事」の内容
# score_co 企業での同種工事の施工実績での配点点数 (str)  　# 要検討：数値化してリスト化
# score_en 技術者での同種工事の施工実績での配点点数 (str)　# 要検討：数値化してリスト化
# 上記表記が見られず、加算点を与える文章表現（例）3.0点／0.0点））に付随した表記の場合は
# その文字列部分を doususei_co[0] doushusei_en[0]に入力する
# 要検討：正規表現での抽出


doushusei_co = list()
doushusei_en = list()

if name_of != "本官": # 本官以外の場合
  if (("より高い同種性が認められる工事：" in text) or ("高い同種性が認められる工事：" in text)):
    # 上記文字列で箇条書き記載がある場合の処理ルーチン 
    t0 = text.partition("企業の能力等（加算点）で提出した企業において") # 後の文字列をタプルとして抽出
    text0 = t0[-1]
    t0 = text0.partition("企業の能力等（加算点）")  #"企業の能力等（加算点）"の後の文字列をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("で評価し、それぞれ") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("の加算点を") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    score_co = text1.strip() # 前後の空白文字を削除
    
    if ("より高い同種性が認められる工事：" in text0):
      t0 = text0.partition("より高い同種性が認められる工事：")  # "より高い同種性が認められる工事："の後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("より高い同種性が認められる工事の実績")  # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushusei_co.insert(0, text1)
    doushusei_co.insert(1, "")
    if ("同種性が認められる工事：" in text0):
      t0 = text0.partition("同種性が認められる工事：")  # "同種性が認められる工事："の後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("共同企業体の構成員")  # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushusei_co.insert(2, text1)
    
    t0 = text0.partition("技術者の能力等（加算点）")  #"技術者の能力等（加算点）"の後の文字列をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("で評価し、それぞれ") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("の加算点を") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    score_en = text1.strip() # 前後の空白文字を削除

    if ("より高い同種性が認められる工事：" in text0):
      t0 = text0.partition("より高い同種性が認められる工事：")  # "より高い同種性が認められる工事："の後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("より高い同種性が認められる工事の実績")  # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushusei_en.insert(0, text1)
    if ("高い同種性が認められる工事：" in text0):
      t0 = text0.partition("同種性が認められる工事：")  # "同種性が認められる工事："の後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("高い同種性が認められる工事の実績")  # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushusei_en.insert(1, text1)
    if ("同種性が認められる工事：" in text0):
      t0 = text0.partition("同種性が認められる工事：")  # "同種性が認められる工事："の後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("共同企業体の構成員")  # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushusei_en.insert(2, text1)

  else: # 配点表記とともに文章内に内容記載がある場合の処理ルーチン
    t0 = text.partition("企業の能力等（")    # "企業の能力等（"文字列の後をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("同種工事の実績において、") # "同種工事の実績において、"の後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("で評価し、") # "で評価し、"の前の文字列をタプルとして抽出
    text1 = t1[0]
    doushusei_co.insert(0,text1)
    t0 = text0.partition("、それぞれ")  # "、それぞれ"の後の文字列をタプルとして抽出
    text1 = t0[-1]
    t1 = text1.partition("の加算点を与える。")  # "の加算点を与える。"の前の文字列をタプルとして抽出
    text1 = t1[0]
    score_co = text1

    t0 = text0.partition("技術者の能力等（") # "配置予定技術者の能力等（"の後の文字列をタプルとして抽出
    text0 = t0[-1]
    if ("補佐の場合において、" in text0):
      t1 = text0.partition("補佐の場合において、")  # "補佐の場合において、"の後の文字列をタプルとして抽出
      text1 = t1[-1]
    if("補助者の場合において、" in text0):
      t1 = text0.partition("補助者の場合において、") # "補助者の場合において、"の後の文字列をタプルとして抽出
      text1 = t1[-1]
    t1 = text1.partition("で評価し、") # "で評価し、"の前の文字列をタプルとして抽出
    text1 = t1[0]
    doushusei_en.insert(0,text1)
    t1 = text0.partition("で評価し、") # "で評価し、"の後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("の加算点を与える。") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    text1 = text1.replace("それぞれ","")  # "それぞれが"が抽出文字列に入っている場合の削除処理"
    score_en = text1

else:  # 本官工事のサブルーチン
  # 企業の能力等（加算点）において記載のある本官工事を探す必要あり！！
  t0 = text.partition("技術者の能力等（")    # 文字列の後をタプルとして抽出
  text0 = t0[-1]
  if ("補佐の場合において、" in text0):
    t1 = text0.partition("補佐の場合において、")  # "補佐の場合において、"の後の文字列をタプルとして抽出
  if("補助者の場合において、" in text0):
    t1 = text0.partition("補助者の場合において、") # "補助者の場合において、"の後の文字列をタプルとして抽出
  if("当技術者の場合において、" in text0):
    t1 = text0.partition("担当技術者の場合において、") # "担当技術"の後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("で評価し、") # "で評価し、"の前の文字列をタプルとして抽出
  text1 = t1[0]
  doushusei_en.insert(0,text1)
  t1 = text0.partition("で評価し、") # "で評価し、"の後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("の加算点を与える。") # 前の文字列をタプルとして抽出
  text1 = t1[0]
  text1 = text1.replace("それぞれ","")  # "それぞれが"が抽出文字列に入っている場合の削除処理"
  score_en = text1


print("「より高い同種性／高い同種性／同種性（企業）list」", doushusei_co)
print("「配点（企業）」", score_co)
print("「より高い同種性／高い同種性／同種性（技術者）list」", doushusei_en)
print("「配点（技術者）」", score_co)



["val1", "val2", "val3"]