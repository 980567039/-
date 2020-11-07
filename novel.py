# coding=utf-8
import requests
import sys, io
from lxml import etree
import pymysql
from time import sleep
BASEURL = 'https://m.biquge5200.cc'

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
db = pymysql.connect("localhost","root","mysqltest","novel" )
cursor = db.cursor()

# 写入数据库
def writeNovel(links, text):
  novelType = text[0].replace('[', '').replace(']', '')
  novelLink = BASEURL + links[1]
  authorLink = BASEURL + links[2]
  sql = """INSERT INTO novel VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', null)""" \
        %(novelType, text[1], text[2], novelLink, authorLink)
  print(sql)
  # 执行sql语句
  cursor.execute(sql)

## 获取所有小说的信息 名称 详情页地址等
def getAllNovel(page):
  res = requests.get('%s/sort-15-%s/' % (BASEURL, page))
  html = etree.HTML(res.text, parser=etree.HTMLParser(encoding='utf-8'))
  elments = html.xpath('//p[@class="line"]')
  for e in elments:
    links = e.xpath('a/@href')
    text = e.xpath('a/text()')
    writeNovel(links, text)
    # print(text)
    # print(links)
  try:
    # 提交到数据库执行
    db.commit()
    print('%s页写入完成' % (page))
  except Exception as e:
    print(e)
    # 如果发生错误则回滚
    db.rollback()


if __name__ == "__main__":
  for i in range(1, 101):
    sleep(1)
    getAllNovel(i)
