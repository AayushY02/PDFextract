# PythonでPDFファイルをテキスト化し、別のフォルダに出力するプログラム
import os
import fitz
import re

# PDFファイルをテキスト化し、別のフォルダに出力する関数
# input_folder (str): 入力フォルダのパス
# output_folder (str): 出力フォルダのパス
def pdf_to_text(input_folder, output_folder):

    for file in os.listdir(input_folder):
        if file.endswith(".pdf"):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file.replace(".pdf", ".txt"))

            fin = fitz.open(input_path)             # open a document
            fout = open(output_path, "wb")          # create a text output
            for page in fin:                        # iterate the document pages
              text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
              # for line in text:                   # 改行行除去処理 test1
              #    text2 = replace(line)
              # text2 = re.sub(r'\n[ ]*\n','', text) # 改行行除去処理 test2
              # text = text2
              out.write(text)                       # write text of page
              fout.write(bytes((12,)))              # write page delimiter (form feed 0x0C)
            fout.close()


# 入力フォルダと出力フォルダを指定
input_folder = "input"
output_folder = "output"

# 関数を実行
pdf_to_text(input_folder, output_folder)

# 改行コードの除去処理
# output_folder2 = "output2"
# text = 
# text2 = re.sub(r'\n[ ]*\n','', text) # 改行行除去処理
# fout2.write(text2)






