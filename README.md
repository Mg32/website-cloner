
Website cloner
==============


なにこれ
--------
指定したウェブサイトからリンクされているページを追跡し、ローカルに完全なコピーを保存します（ただし他ドメインへのリンクは無視します）。
また、各ファイルのハッシュ値 (SHA-1) の一覧も生成します。


必要なもの
----------
- Python 3  
https://www.python.org/
- BeautifulSoup 4  
`$ pip install beautifulsoup4`

使い方
------
`$ python get.py run http://mogesystem.oboroduki.com/index.html`

出力例
------
- get.py
- 170205/ ―― クローンしたファイルの格納先
    - index.html
    - style.css
    - software/
        - index.html
        - 1.png
        - ...
    - ...
- hash-170205.txt ―― ハッシュ値のリスト
