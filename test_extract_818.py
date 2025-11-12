# 818 北海道開発局留萌開発建設部：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
# ★★★　そのままPyMuPDFでテキスト変換すると、「より同種性の高い工事」の　★★★　
# ★★★　テキスト抽出が不可能となるため、一度ＯＣＲで変換する必要あり。　★★★
# 点数配分は、後半部、別表１の表内の文字列を抽出する必要あり。
import re

# inputfile ="T320_入札説明書.txt"
# inputfile ="T321_入札説明書.txt"
# inputfile ="T323_入札説明書.txt"
# inputfile ="T329_入札説明書.txt"
# inputfile ="T332_入札説明書.txt"
# inputfile ="T333_入札説明書.txt"
# inputfile ="T334_入札説明書.txt"
# inputfile ="T335_入札説明書.txt"
# inputfile ="T339_入札説明書.txt"
# inputfile ="T341_入札説明書.txt"
inputfile ="T342_入札説明書.txt"


with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(inputfile)
print(len(text))
print("総合評価に関する事項" in text)

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本官工事の場合は「本官」）

if ("北海道開発局留萌開発建設部" in text):
  name_bu =""

print(name_bu)

if (("支出負担行為担当官" in text) and ("留萌開発建設部長" in text)):  # 本官と分任官とのルーチン分け
  name_of = "北海道開発局留萌開発建設部"
else:  # 事務所名抽出：１つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("北海道開発局留萌開発建設部") # ”北海道開発局留萌開発建設部”の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("所長")                  # "所長"の文字列の前をタプルとして抽出
  text0 = t0[0]
  name_of = text0.strip() + "所"              # 冒頭空白文字を削除して、抽出した文字列に"所"を追加

print(name_of)

# 工事名の抽出
# name_co  工事名 
# (1) 工事名 , (2) 工事場所 で文字列を抽出スライス

t0 = text.partition("工 事 名")  # "工事名"の文字列の後をタプルとして抽出
text0 = t0[-1]
t0 = text0.partition("( 電子入札対象案件) ")  # "（電子入札対象案件）"文字列の前をタプルとして抽出
text0 = t0[0]
name_co =text0.strip()         # 前後の空白文字を削除

print(name_co)


# 同種工事の要件文字列の抽出（企業） doushu_co
# より同種性の高い工事が記載されている場合
# doushu_co01 :「より同種性の高い工事」
# doushu_co02 :「同種工事」または「同種性が認められる工事」

if (("の要件を満たす工事を元請として施工した実績を有すること" in text) 
    and ("当該実績が北海道開発局、" in text)):
  # （４）工事実績の要件記載があるかの判定
  t0 = text.partition("同種工事」の実績とする。")   # 後の文字列をタプルとして抽出
  text0 = t0[-1]
  t1 = text0.partition("【同種性が認められる工事】") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("イ【より同種性の高い") # 文字列の前をタプルとして抽出
  text1 = t1[0]
  text1 = text1.replace("　","") # 空白文字の除去
  text1 = re.sub(r'。\d', '。', text1) # 文字列末尾にページ番号数字が入っている場合の除去処理
  doushu_co = text1
  doushu_co02 = text1
  
  t1 = text0.partition("【より同種性の高い工事】") # 後の文字列をタプルとして抽出
  text1 = t1[-1]
  t1 = text1.partition("(5)") # 文字列の前をタプルとして抽出
  text1 = t1[0]
  text1 = text1.replace("　","") # 空白文字の除去
  text1 = re.sub(r'。\d', '。', text1) # 文字列末尾にページ番号数字が入っている場合の除去処理
  doushu_co01 = text1

  if (("上記( 4) に掲げる工事の経験を有する者であること" in text0) 
      or ("上記(4)に掲げる工事の経験を有する" in text0)):
    doushu_en = doushu_co

  else:
    doushu_en = ""

else:
  doushu_co = "同種条件の記載なし"
  doushu_co01 = ""
  doushu_co02 = ""


# 同種工事の要件文字列の判定（技術者）
# （別表１）の表内において、配置予定技術者としての評価基準の記載がある場合に設定
# doushu_en01 :「より同種性の高い工事」（役職）
# doushu_en02 :「より同種性の高い工事」（役職）「同種性が認められる工事」（役職）
# doushu_en03：「同種性が認められる工事」（役職）
# なお、表中の文字列抽出は行っておらず、各総合評価型での一般的な記載例を設定している。

t0 = text0.partition("別表１評価項目")
text0 = t0[-1]

if (("において、監理( 主任) 技術者、特例監理技術者" in text0) 
    and ("監理技術者補佐又は担当技術者として従事、または" in text0) 
    and ("監監理技術者補佐又は担当技術者として従事") in text0):
  doushu_en01 = "実績より同種性の高い工事において、監理(主任) 技術者、特例監理技術者又は現場代理人として従事"
  doushu_en02 = "より同種性の高い工事において、監理技術者補佐又は担当技術者として従事、または同種性が認められる工事において、監理(主任) 技術者、特例監理技術者又は現場代理人として従事"
  doushu_en03 = "同種性が認められる工事において、監理技術者補佐又は担当技術者として従事"
else:
  doushu_en01 = ""
  doushu_en02 = ""
  doushu_en03 = ""

print("「同種工事（企業）」" ,doushu_co)
print("「同種工事（技術者）」" ,doushu_en)
print("「より同種性の高い工事（企業）」" ,doushu_co01)
print("「同種工事（企業）」", doushu_co02)
print("「より同種性の高い工事（技術者）」" ,doushu_en01)
print("「より同種性の高い工事・同種工事（技術者）」", doushu_en02)
print("「同種工事（技術者）」", doushu_en03)
