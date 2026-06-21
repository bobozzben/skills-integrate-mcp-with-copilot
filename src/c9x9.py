# c9x9.py: 九九乘法表生成器

import os, sys

# 導入 Flask 模組（如果尚未安裝，請先執行 pip install flask）
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# 設定 Google OAuth2 密碼
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
sys.path.append(os.path.dirname(__file__))

def generate_9x9_multiplication_table():
    """
    Generates and prints the complete 9×9 multiplication table.
    Each line displays an equation in the format "a × b = result", covering all combinations from a=1 to 9, b=1 to 9.
    Follows PEP8 style guidelines for readability and consistency.
    """
    
    # 使用嵌套迴圈遍歷數字 1-9
    output_lines = []
    for a in range(1, 10):
        line_parts = [f"{a} × {b} = {a * b}" for b in range(1, 10)]
        formatted_line = "\t".join(line_parts)
        output_lines.append(formatted_line)
    
    # 輸出每行結果
    for line in output_lines:
        print(line)

@app.route('/')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    generate_9x9_multiplication_table()
    """
    Generates and prints the complete 9×9 multiplication table.
    Each line displays an equation in the format "a × b = result", covering all combinations from a=1 to 9, b=1 to 9.
    Follows PEP8 style guidelines for readability and consistency.
    """
    
    # 使用嵌套迴圈遍歷數字 1-9
    output_lines = []
    for a in range(1, 10):
        line_parts = [f"{a} × {b} = {a * b}" for b in range(1, 10)]
        formatted_line = "\t".join(line_parts)
        output_lines.append(formatted_line)
    
    # 輸出每行結果
    for line in output_lines:
        print(line)

if __name__ == "__main__":
    generate_9x9_multiplication_table()