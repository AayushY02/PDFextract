# 810 北海道開発局札幌開発建設部：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
# 評価基準までは別表イの別のPDFから表内表記を読み込む必要あり
import re


# inputfile = "1157入札説明書.txt"
# inputfile = "2047入札説明書.txt"
# inputfile = "2048入札説明書.txt"
# inputfile ="2050入札説明書.txt"
# inputfile = "８６０６　入札説明書　一般国道２３１号　石狩市　嶺泊スノーシェルター補修外一連工事.txt"
inputfile ="８６１０　入札説明書　道央圏連絡道路　南幌町　南７線舗装外一連工事.txt"

with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(inputfile)
print(len(text))
print("総合評価に関する事項" in text)

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本官工事の場合は「本官」）

if ("北海道開発局札幌開発建設部" in text):
  name_bu =""

print(name_bu)

print ("支出負担行為担当官北海道開発局札幌開発建設部長" in text)  # 本官と分任官とのルーチン分け
if ("支出負担行為担当官北海道開発局札幌開発建設部長" in text):  # 本官と分任官とのルーチン分け
  name_of = "北海道開発局札幌開発建設部"
else:  # 事務所名抽出：１つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("北海道開発局札幌開発建設部") # ”北海道開発局札幌開発建設部”の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("所長")                  # "所長"の文字列の前をタプルとして抽出
  text0 = t0[0]
  name_of = text0.strip() + "所"              # 冒頭空白文字を削除して、抽出した文字列に"所"を追加

print(name_of)

# 工事名の抽出
# name_co  工事名 
# (1) 工事名 , (2) 工事場所 で文字列を抽出スライス
if ("(電子入札対象案件)" in text): # ()の半角・全角処理
  name_end = "(電子入札対象案件)"
elif ("（電子入札対象案件）" in text):
  name_end = "（電子入札対象案件）"

t0 = text.partition("工事名")  # "工事名"の文字列の後をタプルとして抽出
text0 = t0[-1]
t0 = text0.partition("(2)")    # 次行にある(2)の文字列の前をタプルとして抽出
text0 = t0[0]
t0 = text0.partition(name_end)  # "（電子入札対象案件）"文字列の前をタプルとして抽出
text0 = t0[0]
name_co =text0.strip()         # 前後の空白文字を削除

print(name_co)

# 同種工事の要件文字列の抽出（企業） doushu_co
# より同種性の高い工事が記載されている場合
# doushu_co01 :「より同種性の高い工事」
# doushu_co02 :「同種性が認められる工事」

if (("施工した実績を有すること" in text) 
    and ("当該実績が北海道開発局、" in text)):
  # （４）工事実績の要件記載があるかの判定
  t0 = text.partition("点未満のものを除く。")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  if (("①【同種条件】" in text0) and ("②【より同種性の高い" in text0)):
    # ①【同種条件】、②【より同種性の高い工事条件】と列記している場合
    t1 = text0.partition("①【同種条件】") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("(施工実績が確認") # 文字列の前をタプルとして抽出
    text1 = t1[0]
    doushu_co = text1
    doushu_co02 = text1

    t1 = text0.partition("②【より同種性の高い工事条件】") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("(施工実績が確認") # 文字列の前をタプルとして抽出
    text1 = t1[0]
    doushu_co01 = text1

  elif ("①【同種条件】" in text0):
    # ①【同種条件】のみ列記している場合
    t1 = text0.partition("①【同種条件】") # 後の文字列をタプルとして抽出
    text1 = t1[-1]
    t1 = text1.partition("(施工実績が確認") # 文字列の前をタプルとして抽出
    text1 = t1[0]
    doushu_co = text1
    doushu_co01 = ""
    doushu_co02 = ""
  else:
    doushu_co = "同種条件の記載なし"
else:
  doushu_co = "工事実績の要件記載なし"

if ("上記(4)本文に掲げる工事の経験を有する者であること" in text):
  doushu_en = doushu_co
elif (("上記(4)本文に掲げる工事を" in text) and "を有する者であること" in text):
  doushu_en = doushu_co
else:
  doushu_en = "工事実績の要件記載なし"

# 技術者での同種工事、より同種性の高い工事の評価については、
# 別表の他のPDFファイルを参照する必要あり（未対応）

print("「同種工事（企業）」" ,doushu_co)
print("「同種工事（技術者）」" ,doushu_en)
print("「より同種性の高い工事（企業）」" ,doushu_co01)
print("「同種工事（企業）」", doushu_co02)
