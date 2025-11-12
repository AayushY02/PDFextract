## test pdfminer.sixによるPDF変換テキストの
## リストへの格納と文字列抽出・操作のテスト

## pdfminer.sixモジュールクラスインポート　
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO
import re
import os


## 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
inputfile = "pdfminer_sample1.pdf"
fin = open(inputfile, 'rb')

# 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
outputfile = "output_sample1.txt"
outputfile2 = "output_sample2.txt"
fout = open(outputfile, 'w', encoding="utf-8")
fout2 = open(outputfile2, 'w', encoding="utf-8")

# 出力先をPythonコンソールするためにIOストリームを取得
outfp = StringIO()


# 各種テキスト抽出に必要なPdfminer.sixのオブジェクトを取得する処理

rmgr = PDFResourceManager() # PDFResourceManagerオブジェクトの取得
lprms = LAParams()          # LAParamsオブジェクトの取得
device = TextConverter(rmgr, outfp, laparams=lprms)    # TextConverterオブジェクトの取得
iprtr = PDFPageInterpreter(rmgr, device) # PDFPageInterpreterオブジェクトの取得

# PDFファイルから1ページずつ解析(テキスト抽出)処理する
for page in PDFPage.get_pages(fin):
    iprtr.process_page(page)

fout.write(outfp.getvalue())  ## テキストファイルへの書き出し
text = outfp.getvalue()  # Pythonコンソールへの出力内容を取得
print(len(text))
print(re.search("関東地方整備局", text))

text2 = re.sub(r'\n[ ]*\n','', text) # 改行行除去処理
fout2.write(text2)
print(len(text2))
print(re.search("関東地方整備局", text2))

new_func(fout2, text)

outfp.close()  # I/Oストリームを閉じる
device.close() # TextConverterオブジェクトの解放
fin.close()    # Fileストリームを閉じる
fout.close()   # Fileストリームを閉じる
fout2.close()  # Fileストリームを閉じる




# print(text)  # Jupyterの出力ボックスに表示する