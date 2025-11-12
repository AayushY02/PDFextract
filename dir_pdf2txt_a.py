# PythonでPDFファイルをテキスト化し、別のフォルダに出力するプログラム

import os
from pdfminer.high_level import extract_text


def pdf_to_text(input_folder, output_folder):
    """
    PDFファイルをテキスト化し、別のフォルダに出力する関数

    Args:
        input_folder (str): 入力フォルダのパス
        output_folder (str): 出力フォルダのパス
    """

    for file in os.listdir(input_folder):
        if file.endswith(".pdf"):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file.replace(".pdf", ".txt"))

            with open(output_path, 'w', encoding='utf-8') as text_file:
                text = extract_text(input_path)
                text_file.write(text)

# 入力フォルダと出力フォルダを指定
input_folder = "input"
output_folder = "output"

# 関数を実行
pdf_to_text(input_folder, output_folder)

