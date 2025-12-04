# フォルダ内のPDFファイルをテキスト化し、別のフォルダに出力するプログラム

import os
import fitz  # pymupdfライブラリのインポート
import re


# PDFファイルをテキスト化し、別のフォルダに出力する関数定義：pdf_to_text 
#   input_folder (str): 入力フォルダのパス
#   output_folder (str): 出力フォルダのパス
def pdf_to_text(input_folder, output_folder):
    for file in os.listdir(input_folder):
        if file.endswith(".pdf"):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file.replace(".pdf", ".txt"))

            fin = fitz.open(input_path)             # open a document
            fout = open(output_path, "wb")          # create a text output
            for page in fin:                        # iterate the document pages
              text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
              fout.write(text)                      # write text of page
              fout.write(bytes((12,)))              # write page delimiter (form feed 0x0C)
            fout.close()

# 抽出したテキストファイルからページ番号文字列、改ページコード、改行コードを除去する関数定義：del_text_n
#   input_folder (str): 入力フォルダのパス
#   output_folder (str): 出力フォルダのパス
def del_text_n(input_folder, output_folder):
    for file in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, file)

        fin = open(input_path, "r", encoding="utf-8")
        fout = open(output_path, "w", encoding="utf-8")
        for page in fin:
            text = re.sub(r'- \d{,3} -', '',  page)  # ページ番号文字列除去（最大３桁）
            text = re.sub(r'\f', '', text)           # 改ページコードの除去
            text = re.sub(r'\n', '', text)           # 改行コードの除去
                                                     ### text = ''.join(page.splitlines())
                                                     ### text = re.sub(r"\n[ ]*\n","",page)
            fout.write(text)
        fin.close()
        fout.close()



# 入力フォルダと出力フォルダを指定
input_folder = "input_old"
output_folder = "output"
output_folder2 = "output2"

# 関数を実行
pdf_to_text(input_folder, output_folder)
del_text_n(output_folder, output_folder2)
print("テキスト出力が完了しました")






