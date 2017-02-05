#!/usr/bin/env python
#-*- coding:utf-8 -*-

from urllib.request import urlretrieve
from urllib.parse import urlparse, urljoin
from datetime import datetime
from bs4 import BeautifulSoup
from collections import deque
import hashlib
import sys
import os
import shutil

# Website cloner for Python 3
# 指定ページからリンクされている同ドメイン上のファイルを一括ダウンロードする。
# リンクを探索するHTMLタグは以下のとおり。
searchElements = {
    'link': 'href',
    'script': 'src',
    'a': 'href',
    'img': 'src',
    'frame': 'src'
}

# 準備
# $ pip install beautifulsoup4

# 使い方
# $ python get.py run http://mogesystem.oboroduki.com/index.html
# $ python get.py clean
# $ python get.py clean 170205

def combineURL(base, url):
    return urljoin(base, url)

def getURLDomain(url):
    return urlparse(url).netloc

def getURLFilename(origin, url):
    l = combineURL(origin, './')
    return url.replace(l, '')

def combineFilePath(base, path):
    return os.path.normpath(os.path.join(base, path))

def getFileDirectory(filename):
    root, name = os.path.split(filename)
    return root

def getFileExt(filename):
    root, ext = os.path.splitext(filename)
    return ext

def isHTML(filename):
    return getFileExt(filename) in {'.html', '.htm'}

#

def readFile(filename):
    with open(filename, 'r') as f:
        doc = f.read()
    return doc

def readFileBinary(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return data

def writeFile(filename, doc):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(doc)

def isPathExist(path):
    return os.path.exists(path)

def deleteFile(filename):
    if isPathExist(filename):
        os.remove(filename)

def createDir(path):
    if not isPathExist(path):
        os.mkdir(path)

def deleteDir(path):
    if isPathExist(path):
        shutil.rmtree(path)

#

def getNowString():
    return datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def generateArchiveID():
    return datetime.now().strftime('%y%m%d')

def getDownloadPath(aid):
    return combineFilePath(os.getcwd(), aid)

def getLogFileName(aid):
    return combineFilePath(os.getcwd(), 'hash-' + aid + '.txt')

#

def downloadFile(url, filename):
    urlretrieve(url, filename)

def getSHA1(filename):
    d = readFileBinary(filename)
    return hashlib.sha1(d).hexdigest().upper()

def scrapeLinksFromHTML(url, html_doc, elemDict):
    soup = BeautifulSoup(html_doc, 'html.parser')
    links = []
    for name, attr in elemDict.items():
        for elm in soup.find_all(name):
            links.append(combineURL(url, elm.get(attr)))
    return links

def chainDownloadWithHash(url, path):
    domain_orig = getURLDomain(url)
    found = set()
    hashdict = {}
    q = deque([url])
    while len(q) != 0:
        src = q.popleft()
        dst = combineFilePath(path, getURLFilename(url, src))
        createDir(getFileDirectory(dst))

        print('Downloading', src)
        downloadFile(src, dst)
        found.add(src)
        hashdict[src] = getSHA1(dst)

        if not isHTML(dst):
            continue
        doc = readFileBinary(dst)
        scraped = scrapeLinksFromHTML(src, doc, searchElements)
        for u in (set(scraped) - set(found)):
            if domain_orig != getURLDomain(u):
                continue
            found.add(u)
            q.append(u)

    return hashdict

#

def writeLogFile(filename, url, hashdict, time_begin, time_end):
    timestr = '開始時刻: {0}\n終了時刻: {1}\n'.format(time_begin, time_end)
    hashstr = 'ハッシュアルゴリズム: SHA-1\n'
    for u, h in sorted(hashdict.items(), key=lambda x : x[0]):
        hashstr += '{0:<80}{1}\n'.format(u, h)
    out = 'URL: {0}\n{1}{2}'.format(url, timestr, hashstr)
    writeFile(filename, out)

#

def run(aid, url):
    print('From:\t', url)

    path = getDownloadPath(aid)
    createDir(path)
    print('To:\t', path, '\n')

    time_begin = getNowString()
    hashdict = chainDownloadWithHash(url, path)
    time_end = getNowString()
    print('\nDownloaded', url, 'to', aid)

    logname = getLogFileName(aid)
    writeLogFile(logname, url, hashdict, time_begin, time_end)
    print('Log:', logname)

def clean(aid):
    deleteDir(getDownloadPath(aid))
    deleteFile(getLogFileName(aid))
    print('Cleaned', aid)

#

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 2:
        exit()

    aid = generateArchiveID()
    if sys.argv[1] == 'run':
        if argc < 3:
            print('run: URLを指定してください')
            exit()
        url = urlparse(sys.argv[2]).geturl()
        run(aid, url)
    elif sys.argv[1] == 'clean':
        if argc >= 3:
            aid = sys.argv[2]
        clean(aid)
    else:
        print('コマンド', sys.argv[1], 'を認識できません。')
