# coding=utf-8
import requests
import sys, io, time, random
from lxml import etree
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
db = pymysql.connect("localhost","root","mysqltest","novel" )
cursor = db.cursor()

def run():
    sql = "select content_id, id from chapter where spider=0"
    cursor.execute(sql)
    spiderList = cursor.fetchall()
    for idx, item in enumerate(spiderList):
        time.sleep(1)
        url = 'https://m.biquge5200.cc/%s/' % item[0]
        res = requests.get(url)
        html = etree.HTML(res.text, parser=etree.HTMLParser(encoding='utf-8'))
        content = html.xpath('//div[@class="text"]')[0].xpath('string(.)')
        writeContent(content, item[1])
        if(idx % 20 == 0 and idx != 0):
            try:
                # 提交到数据库执行
                db.commit()
                print('提交成功')
                sys.stdout.flush()
            except Exception as e:
                print(e)
                # 如果发生错误则回滚
                db.rollback()

def writeContent(content, id):
    sql = """INSERT INTO content VALUES ( null, \'%s\', \'%s\')""" % (content, id)
    cursor.execute(sql)
    setSql = 'update chapter set spider=1 where id=%s' % id
    cursor.execute(setSql)
    
if __name__ == "__main__":
  run()
  cursor.close()