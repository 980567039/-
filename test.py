# coding=utf-8
import requests
import sys, io, time, re
from lxml import etree
import pymysql
BASEURL = 'https://m.biquge5200.cc'

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
db = pymysql.connect("localhost","root","mysqltest","novel" )
cursor = db.cursor()

def filterStr(str, lst):
  d = str.replace('【】', '')
  for t in lst:
    d = d.replace(t, '')
  return d

def test():
  sql = 'SELECT id, content FROM content'
  cursor.execute(sql)
  lst = cursor.fetchall()
  for inx, item in enumerate(lst):
    # print('-----------------------')
    pattern = re.compile(r'try.*?\{}')
    temp = re.findall(pattern, item[1])
    str = filterStr(item[1], temp)
    updateSql = ''' UPDATE content SET content=\'%s\' WHERE id=%s ''' % (str, item[0])
    cursor.execute(updateSql)
    print(inx)
  db.commit()
  db.close()


if __name__ == "__main__":
  test()