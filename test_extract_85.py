# 85中部地整：入札説明書（PDF）から「より同種性が高い」工事要件を抽出するテストプログラム
import re

inputfile = "test_85_true.txt"
# inputfile = "【公告・入札説明書】令和５年度　高山国道管内トンネル照明設備工事.txt"
# inputfile = "【公告・入札説明書】令和５年度　高山国道区画線維持工事.txt" #　！事務所名抽出出来ず！
# inputfile = "【入札公告・入札説明書】令和5年度 設楽ダム国道257号田口地区道路建設工事.txt"
# inputfile = "【公告・入札説明書】令和５年度　４１号高山国府トンネル換気設備整備工事.txt"
# inputfile = "静岡河川01_setsumeisyo.txt"
# inputfile = "説明書　令和５年度　設楽ダム本体建設第１期工事.txt"
# inputfile = "説明書　令和５年度 一般県道松原芋島線川島大橋橋脚工事.txt"
# inputfile = "説明書　令和５年度　１号清水立体尾羽第１高架橋鋼上部工事　他.txt"

with open(inputfile, "rt", encoding="utf-8") as f:  # 改行コード等除去後のテキストファイルを開く
  text = f.read()

print(len(text))
print("入札の評価に関する基準及び得点配分" in text)

# 入札公告が先頭部部分にある場合、入札説明書のページ以降を抽出する
# if (("入札公告（建設工事）" in text) and text.find("入札公告（建設工事）") <20 ):
#   t = text.partition("④  開札日時")  # 入札公告の最終ページの記載文をタプルとして抽出
#   print(t[1] == '')
#   print(t[2] == '')
#   text = t[-1]                       # 以降の文字列を抽出
#   t = text.partition("入札説明書")   # 入札説明書の１ページ目の記載文
#   text = t[-1]                       # 以降の文字列を抽出（入札説明書の部分（行頭欠け））

# print(len(text))

# 整備局等名・事務所名の抽出
# namu_bu 地方整備局等
# name_of 事務所名（本館工事の場合は「本官」）
name_bu="not found"
if ("中部地方整備局" in text):
  name_bu ="中部地方整備局"

print(name_bu)

# print(("支出負担行為担当官 中部地方整備局長" in text))  # 本官と分任官工事とのルーチン分け
if ("支出負担行為担当官 中部地方整備局長" in text):  # 本官と分任官とのルーチン分け
  name_of = "本官"
else:  # 事務所名抽出：２つめの分任支出負担行為担当官以下の　所長までの部分でスライス
  t0 = text.partition("分任支出負担行為担当官")  # 入札説明書の１つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("分任支出負担行為担当官") # 入札説明書の２つめの同一文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("中部地方整備局")        # ”中部地方整備局”の前半をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("所長")                  # "所長"の文字列の前をタプルとして抽出
  text0 = t0[0]
  name_of = text0.strip() + "所"              # 冒頭空白文字を削除して、抽出した文字列に"所"を追加

print(name_of)

# 工事名の抽出
# name_co 工事名
# (1) 工事名 , (2) 工事場所 で文字列を抽出スライス

t0 = text.partition("工事名")  # "工事名"の文字列の後をタプルとして抽出
text0 = t0[-1]
t0 = text0.partition("(2)")    # 次行にある(2)の文字列の前をタプルとして抽出
text0 = t0[0]
t0 = text0.partition("（電子入札対象案件）")  # "（電子入札対象案件）"文字列の前をタプルとして抽出
text0 = t0[0]
name_co =text0.strip()         # 前後の空白文字を削除

print(name_co)

# 同種工事の内容　入札説明書　４）競争参加資格の項目より抽出　【企業】同種工事、【技術者】同種工事
# doushu_co 企業での同種工事の内容
# doushu_en 技術者での同種工事の内容
# 本官工事での場合で【企業】【技術者】の文字列がない場合は「特殊工事のため要確認」を入力
# 要検討：正規表現での抽出

if name_of != "本官": # 本官以外の場合
  t0 = text.partition("元請けとして、以下に示す同種工事")  #"元請けとして、以下に示す同種工事"の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("【企業】") # "【企業】"の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("同種工事：") # "同種工事："の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("【技術者】") # "【技術者】"の前の文字列をタプルとして抽出
  text0 = t0[0]
  doushu_co = text0.strip() # 前後の空白文字を削除
  print("「同種工事（企業）」", doushu_co)
  text0 = t0[-1]  # "技術者"の後の文字列を入力
  t0 = text0.partition("同種工事：")  # "同種工事："の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("(5)") # (5)の前の文字列をタプルとして抽出
  text0 = t0[0]
  doushu_en = text0
  print("「同種工事（技術者）」", doushu_en)

elif (("【企業】" in text) and ("【技術者】") in text): # 抽出する文字列２つがある場合のサブルーチン
  print("here")
  t0 = text.partition("発注者から企業に対して通知された評定点が")    # 文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("【企業】") # "【企業】"の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("同種工事：") # "同種工事："の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("【技術者】") # "【技術者】"の前の文字列をタプルとして抽出
  text0 = t0[0]
  doushu_co = text0.strip() # 前後の空白文字を削除
  print(doushu_co)
  print("「同種工事（企業）」", doushu_co)
  text0 = t0[-1]  # "技術者"の後の文字列を入力
  t0 = text0.partition("同種工事：")  # "同種工事："の後の文字列をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("(5)") # (5)の前の文字列をタプルとして抽出
  text0 = t0[0]
  t0 = text0.partition("(6)") # (6)の前の文字列をタプルとして抽出
  text0 = t0[0]
  doushu_en = text0.strip()
  print("「同種工事（技術者）」", doushu_en)

else:  # 企業・技術者の表記がない場合のサブルーチン
  t0 = text.partition("発注者から企業に対して通知された評定点が")    # 文字列の後をタプルとして抽出
  text0 = t0[-1]
  t0 = text0.partition("同種工事：") # "同種工事："の後の文字列をタプルとして抽出
  text0 = t0[-1]
  print(text0)
  t0 = text0.partition("(6)") # (6)の前の文字列をタプルとして抽出
  text0 = t0[0]
  doushu_co = text0.strip() # 前後の空白文字を削除
  print("「同種工事（企業）」", doushu_co)
  doushu_en = "特殊工事のため要確認"
  print("「同種工事（技術者）」", doushu_en)


# 「より同種性が高い」工事の要件抽出
# souahu01 str
# (3) 入札の評価に関する基準及び得点配分
# 工事の総合評価に関する加算点の表外にある記載「※１：同種工事の内・・・・を「より同種性が高い」の部分文字列を抽出

if (("※１：" in text) and ("を「より同種性が高い」と評価" in text)):  # 記載があるかの判定
  t1 = text.partition("※１：")   # "※１："の文字列の後
  text1 = t1[-1]
#  print(t1[-1])
  t1 = text1.partition("同種工事のうち、")
  text1 =t1[-1]
#  print(t2[-1])
  t1 = text1.partition("を「より同種性が高い」と評価")
  text1 =t1[0]
else:
  text1 = "該当なし"

doushu01 = text1
print("「より同種性の高い」", doushu01)
