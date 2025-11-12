#90 沖縄総合事務局：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
import re


inputfile = "【入札説明書】令和5年祖宜名真情報板外設置工事.txt"
# inputfile = "【入札説明書】令和５年度　海洋博公園電気設備改修工事.txt"
# inputfile = "【入札説明書】令和5年度安波ダム系管理用制御処理設備設置工事.txt"
# inputfile = "【入札説明書】令和５年度羽地地区交通安全対策工事.txt"
# inputfile = "【入札説明書】令和5年度恩納BP４号橋下部工(下りA1・P1)工事.txt"
# inputfile = "【入札説明書】令和５年度恩納BP６号橋上部工（下りA1～P4）工事.txt"
# inputfile = "【入札説明書】令和5年度恩納南ＢＰ改良工事.txt"
# inputfile = "【入札説明書】令和５年度宜名真トンネルラジオ再放送設備設置工事.txt"
# inputfile = "【入札説明書】令和５年度国道３３２号植栽整備（その１）工事.txt"
# inputfile = "【入札説明書】令和５年度佐敷地区安全施設設置工事.txt"
# inputfile = "【入札説明書】令和５年度前兼久南地区電線共同溝設置工事.txt"
# inputfile = "【入札説明書】令和5年度北部国道管内交通安全対策工事.txt"
# inputfile = "【入札説明書】令和5年度北部国道管内保全(その１)工事.txt"


with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(inputfile)
print(len(text))
print("総合評価に関する事項" in text)

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本官工事の場合は「本官」）

if ("沖縄総合事務局" in text):
  name_bu =""

print(name_bu)

print ("支出負担行為担当官沖縄総合事務局開発建設部長" in text)  # 本官と分任官とのルーチン分け
if ("支出負担行為担当官沖縄総合事務局開発建設部長" in text):  # 本官と分任官とのルーチン分け
  name_of = "本官"
else:  # 事務所名抽出：１つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("沖縄総合事務局")        # ”沖縄総合事務局”の前半をタプルとして抽出
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

if (("「同種工事」は、次の要件を満たす" in text) and ("同種工事とは４．（４）に明示" in text)):
   # 「「同種工事」は、次の要件を満たす施工実績を有すること」記述への対応（公園事務所のＣＣＴＶ工事）
  t0 = text.partition("次に掲げる施工実績を有すること。")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  if ("「同種工事」は" in text):
    t1 = text0.partition("「同種工事」は、次の要件を満たす施工実績を有すること。・")
  t1 = text1.partition("※施工実績が確認できる資料(コリンズ") # 文字列の前をタプルとして抽出 
  text1 =t1[0]

elif ("・同種工事" in text) and ("・より同種工事" in text):  # ・同種工事　・より同種工事と箇条書き記述への対応
  t0 = text.partition("次の要件を満たす施工実績を有すること。")
  text0 = t0[-1]
  t1 = text0.partition("・同種工事：") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("・より同種工事：") # 文字列の前をタプルとして抽出
  text1 = t1[0]

elif ("同種工事：" in text): # 同種工事：との記述への対応
  t0 = text.partition("次の要件を満たす施工実績を有すること。")
  text0 = t0[-1]
  t1 = text0.partition("同種工事：") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("※コリンズで") # 文字列の前をタプルとして抽出
  text1 = t1[0]

elif (("次の(ｱ)、(ｲ)の要件を満たす施工実績を有すること。" in text) and ("同種工事とは４．（４）に明示" in text)):
  # 同種工事として(ｱ)、(ｲ)との箇条書き記述への対応
  t0 = text.partition("次に掲げる施工実績を有すること。")
  text0 = t0[-1] # 後の文字列をタプルとして抽出
  t1 = text0.partition("(ｲ)の要件を満たす施工実績を有すること。")
  text1 = t1[-1] # 後の文字列をタプルとして抽出
  t1 = text1.partition("※コリンズで")  # 文字列の前をタプルとして抽出
  text1 = t1[0]

elif (("次の要件を満たす施工実績を有すること" in text) and ("同種工事とは４．（４）に明示" in text)) :  # 記載があるかの判定
  t0 = text.partition("次の要件を満たす施工実績を有すること")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  if ("同種工事：" in text0):  # 同種工事と箇条書き記述への対応
    t1 = text0.partition("同種工事：" in text0) # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1
  else:
    t1 = text0.partition("・") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
  t1 = text1.partition("※コリンズで") # 文字列の前をタプルとして抽出 
  text1 =t1[0]

else:
  text1 = "記載なし"

doushu_co = text1


#　同種工事の要件文字列の抽出（技術者） doushu_en
if (("工事に専任で配置できること" in text) 
    and 
    (("に掲げる同種工事の要件を満たす工事現場に従事した経験を有する者") in text )
    or ("に掲げる要件の施工経験を有する者であること。")):
  # 技術者への同種工事の経験を有する記載があるかの判定
  doushu_en = doushu_co
else:
  doushu_en = "記載なし"


print("「同種工事（企業）」", doushu_co)
print("「同種工事（技術者）」", doushu_en)


# より同種性の高い工事／同種性が認められる工事の内容の抽出
# 2)評価基準及び得点配分 ①－１企業の能力等（加算点１）及び
# ②配置予定技術者の能力等（加算点２）の表外の記載からそれぞれの内容を抽出する
# doushusei_co01 企業での「より高い同種性の高い工事」の内容
# doushusei_co02 企業での「同種工事」の内容 
# doushusei_en01 技術者での「より高い同種性の高い工事」の内容
# doushusei_en02 技術者での「同種工事」の内容
# 配点は表内にマトリックスで記載されているが抽出方法は要検討
# score_en 技術者での同種工事の施工実績での配点点数 (str)　# 要検討：表内抽出
# score_co 企業での同種工事の施工実績での配点点数 (str)  　# 要検討：表内抽出


if name_of != "本官": # 本官以外の場合
  if (("同種工事とは" in text) and ("より同種工事とは" in text)):
    if ("同種工事：" in text) and ("より同種工事：" in text):
    # 上記文字列で表外記載がある場合の処理ルーチン
      t0 = text0.partition("同種工事とは４") # "企業の能力等（加算点１）"後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("同種工事：")  # "）に明示しているとおりである。"の後の文字列をタプルとして抽出
      text1 = t1[-1]
      t1 = text1.partition("◇より同種工事とは") # 文字列の前をタプルとして抽出 
      text1 = t1[0]
      doushu_co02 = text1
      t0 = text0.partition("より同種工事とは、") # 後の文字列を抽出
      text0 = t0[-1]
      t1 = text0.partition("より同種工事：") # 後の文字列をタプルとして抽出
      text1 = t1[-1]
      t1 = text1.partition("◇施工実績") # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushu_co01 = text1
     
    else:
      t0 = text0.partition("同種工事とは４") # "企業の能力等（加算点１）"後の文字列をタプルとして抽出
      text0 = t0[-1]
      t1 = text0.partition("）に明示しているとおりである。・")  # "）に明示しているとおりである。"の後の文字列をタプルとして抽出
      text1 = t1[-1]
      t1 = text1.partition("◇より同種工事とは") # 文字列の前をタプルとして抽出 
      text1 = t1[0]
      doushu_co02 = text1
      t0 = text0.partition("より同種工事とは、") # 後の文字列を抽出
      text0 = t0[-1]
      t1 = text0.partition("次のとおりとする。・") # 後の文字列をタプルとして抽出
      text1 = t1[-1]
      t1 = text1.partition("◇施工実績") # 前の文字列をタプルとして抽出
      text1 = t1[0]
      doushu_co01 = text1

else: # 本官工事の場合
  if ("同種工事：" in text) and ("より同種工事：" in text):
  # 上記文字列で表外記載がある場合の処理ルーチン
    t0 = text0.partition("同種工事とは４") # "企業の能力等（加算点１）"後の文字列をタプルとして抽出
    text0 = t0[-1]
    t1 = text0.partition("同種工事：")  # "）に明示しているとおりである。"の後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("◇より同種工事とは") # 文字列の前をタプルとして抽出 
    text1 = t1[0]
    doushu_co02 = text1
    t0 = text0.partition("より同種工事とは、") # 後の文字列を抽出
    text0 = t0[-1]
    t1 = text0.partition("より同種工事：") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("◇施工実績") # 前の文字列をタプルとして抽出
    text1 = t1[0]
    doushu_co01 = text1 

if ("配置予定技術者の能力等（加算点２）" in text0):
  if("配置予定技術者に関する発注機関別の考え方は、施工実績に準ずる"):
    doushu_en01 = doushu_co01
    doushu_en02 = doushu_co02


print("「より同種性の高い（企業）」" ,doushu_co01)
print("「同種工事（企業）」" ,doushu_co02)
print("「より同種性の高い（技術者）」" ,doushu_en01)
print("「同種工事（技術者）」" ,doushu_en02)
