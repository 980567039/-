# coding=utf-8
import requests
import sys, io, time, random
from lxml import etree
import pymysql
BASEURL = 'https://m.biquge5200.cc'

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
db = pymysql.connect("localhost","root","mysqltest","novel" )
cursor = db.cursor()

ua_list = [
  'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
  'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .\
  NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)', ]

headers = {
  'User-Agent': random.choice(ua_list), 
  'Authority': 'm.biquge5200.cc',
  'Cookie': 'Hm_lvt_48b6bcf2e8ec326b3663e20bb30c3754=1604561787; pv=132; cac=61; Hm_lpvt_48b6bcf2e8ec326b3663e20bb30c3754=1604713683',
  'Referer': 'https://m.biquge5200.cc/wapbook-2379_1/',
  'Path': '/wapbook-2379_2/',
  'Scheme': 'https',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Language': 'zh-CN,zh;q=0.9'
}

# 获取总页数
def getPages():
  sql = "select id, novel_link from novel where(spider='0' and type='历史小说') limit 10;"
  cursor.execute(sql)
  result = cursor.fetchall()
  for novel in result:
    novel_key = novel[1].replace('https://m.biquge5200.cc/info-', '').replace('/', '')
    url = novel[1].replace('info', 'wapbook').replace(novel_key, novel_key + '_1')
    res = requests.get(url)
    html = etree.HTML(res.text, parser=etree.HTMLParser(encoding='utf-8'))
    # 章节列表页总页数
    maxPage = html.xpath('//div[@class="page"]')[0].xpath('a/@href')[1].replace('/wapbook-'+novel_key+'_', '').replace('/', '')
    getChapter(novel_key, maxPage, novel[0])

# 获取章节列表
def getChapter(novel_key, maxPage, id):
  for page in range(1, int(maxPage) + 1):
    url = 'https://m.biquge5200.cc/wapbook-%s_%s/' % (novel_key, page)
    res = requests.get(url)
    html = etree.HTML(res.text, parser=etree.HTMLParser(encoding='utf-8'))
    chapterList = html.xpath('//ul[@class="chapter"]/li')
    writeChapter(chapterList, novel_key)
    time.sleep(.5)
  sql = ''' UPDATE `novel` SET `spider`=%s WHERE (`id`=\'%s\') ''' % (1, id)
  cursor.execute(sql)
  try:
    # 提交到数据库执行
    db.commit()
    print('novel %s 所有章节更新完成' % novel_key)
  except Exception as e:
    print(e)
    # 如果发生错误则回滚
    db.rollback()

# 存储章节信息
def writeChapter(chapterList, novel_key):
  for chapter in chapterList:
    link = chapter.xpath('a/@href')[0].replace('/', '')
    title = chapter.xpath('a/text()')[0]
    sql = """INSERT INTO chapter VALUES (null, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')""" \
      %(title, novel_key, link, 0, 0, '20201107110606', '20201107110606')
    cursor.execute(sql)
    print('novel %s 插入新章节 %s' % (novel_key, title))
    sys.stdout.flush()

if __name__ == "__main__":
  getPages()
  cursor.close()