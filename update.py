# coding=utf-8
import requests
import sys, io, time
from lxml import etree
import pymysql
BASEURL = 'https://m.biquge5200.cc'

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
db = pymysql.connect("localhost","root","mysqltest","novel" )
cursor = db.cursor()

def getNovelInfo():
  sql = "select id, novel_link from novel where spider=0"
  cursor.execute(sql)
  result = cursor.fetchall()
  for novel in result:
    time.sleep(0.4)
    novel_link = novel[1]
    res = requests.get(novel_link)
    html = etree.HTML(res.text, parser=etree.HTMLParser(encoding='utf-8'))
    info = html.xpath('//div[@class="block_txt2"]/p/text()')
    status = 1 if info[2] == "状态：连载中" else 0 # 连载状态为1 完结为0
    date = info[3].split('：')[1]
    data = html.xpath('//div[@class="intro_info"]')[0]
    intro = data.xpath('string(.)')
    cover = html.xpath('//div[@class="block_img2"]/img/@src')
    print(cover)
    updateCover(cover[0], novel[0])
    # updateNovel(status, date, intro, novel[0])
  try:
    # 提交到数据库执行
    db.commit()
    print('commit成功')
  except Exception as e:
    print(e)
    # 如果发生错误则回滚
    db.rollback()

def updateNovel(status, t, intro, id):
  sql = ''' UPDATE `novel` SET `status`=\'%s\', `update`=\'%s\', `intro`=\'%s\' WHERE (`id`=\'%s\') ''' % (status, t, intro, id)
  cursor.execute(sql)
  print('id为%s的数据已更新' % id)
  sys.stdout.flush()
  # print(sql)

def updateCover(cover, id):
  sql = ''' UPDATE `novel` SET `cover`=\'%s\' WHERE (`id`=\'%s\') ''' % (cover, id)
  cursor.execute(sql)
  print('id为%s的封面图已更新' % id)
  sys.stdout.flush()

if __name__ == "__main__":
  getNovelInfo()
  cursor.close()