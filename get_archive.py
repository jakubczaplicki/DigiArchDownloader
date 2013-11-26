#
# Download digitized civil registration records (births, marriages, and deaths)
# from State Archive in Olsztyn, Civil Registry Office in Olsztyn
#

import sys, os
import urllib2
import re
import threading, Queue, time

# page 
# od http://olsztyn.ap.gov.pl/baza/skany.php?z=705&s=1
# do http://olsztyn.ap.gov.pl/baza/skany.php?z=705&s=107
# except : 89,90,91

# scan
# http://olsztyn.ap.gov.pl/baza/czytaj.php?skan=0705/00001/01.jpg
# http://olsztyn.ap.gov.pl/baza/czytaj.php?skan=0705/00002/01.jpg

q = Queue.Queue()

class Item():
  def __init__(self, task, threadName, pageNo, scanName):
    self.task = task
    self.threadName = threadName
    self.pageNo = pageNo
    self.scanName = scanName

def worker(id):
  while True:
    if not q.empty():
      item = q.get()
      if (item.task == "html"):
        downloadPage(item.threadName, item.pageNo)
        getListOfScans(item.pageNo)
      elif (item.task == "jpg"):
        downloadScan(item.threadName, item.pageNo, item.scanName)
      elif (item.task == "detect-type"):
        findTemplate(item.threadName, item.pageNo)
      q.task_done()
    else:
      print "Queue empty, Thread: %s" % id;
    time.sleep(1)

def downloadPage(threadName, pageNo):
  print "Downloading %s" % (threadName)
  url = "http://olsztyn.ap.gov.pl/baza/skany.php?z=705&s=%d" % pageNo
  file_name = "%d.html" % pageNo
  dir_name = "%s" % pageNo
  if not os.path.exists(dir_name):
    os.makedirs(dir_name)
  u = urllib2.urlopen(url)
  f = open(dir_name + '/' + file_name, 'wb')
  meta = u.info()
  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
        break
    file_size_dl += len(buffer)
    f.write(buffer)
  f.close()

def downloadScan(threadName, pageNo, scanName):
  print "Downloading %s" % (threadName)
  url = "http://olsztyn.ap.gov.pl/baza/czytaj.php?skan=" + scanName
  file_name = scanName.split('/', 2 )[2]
  dir_name = "%s" % pageNo
  if not os.path.exists(dir_name):
    os.makedirs(dir_name)
  u = urllib2.urlopen(url)
  f = open(dir_name + '/' + file_name, 'wb')
  meta = u.info()
  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
        break
    file_size_dl += len(buffer)
    f.write(buffer)
  f.close()
  #print imghdr.what(file_name)

# analyse downloaded html, choose which jpgs to download (all)
def getListOfScans(pageNo):
  file_name = "%d.html" % pageNo
  dir_name = "%d" % pageNo
  f = open(dir_name + '/' + file_name, 'r')
  str = f.read()
  f.close()
  regex = re.compile("czytaj.php\?skan=([0-9]+\/[0-9]+\/[0-9]+.jpg)")
  scans = regex.findall(str) 
  for scanname in scans:
    threadName = "JPG-thread-%s" % scanname
    item = Item("jpg", threadName, pageNo, scanname)
    q.put(item)

def download():
  for i in range(10):
    t = threading.Thread(target=worker, args = [i])
    t.daemon = True
    t.start()
  #lista = list(xrange(1,108))
  #lista = lista[:88] + lista[91:]
  lista = list(xrange(89,92))
  for pageNo in lista:
    threadName = "HTML-thread-%d" % pageNo
    item = Item("html", threadName, pageNo, '')
    q.put(item)
  q.join()

download()
