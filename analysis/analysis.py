#
# Detect the record type (births, marriages, and deaths) 
# Run this script AFTER downloading the scans.

import sys, os
import urllib2
import re
import threading, Queue
import cv2
import time

q = Queue.Queue()

class Item():
  def __init__(self, task, threadName, pageNo, scanName):
    self.task = task
    self.threadName = threadName
    self.pageNo = pageNo
    self.scanName = scanName

def worker():
  while True:
    item = q.get()
    if (item.task == "detect-type"):
      findTemplate(item.threadName, item.pageNo)
    q.task_done()
    time.sleep(1000)
    if len(q) == 0:
      return;

def findTemplate(threadName, pageNo):
  print "Analysing %s" % (threadName)
  fname = '%d/00.jpg' % pageNo
  if not os.path.exists(fname):
    fname = '%d/000.jpg' % pageNo
    if not os.path.exists(fname):
      result = -1
  img_rgb = cv2.imread(fname,0)
  #img2 = img_rgb.copy()
  template = cv2.imread('template_urodzen.png',0)
  w, h = template.shape[::-1]
  #img_rgb = img2.copy()
  res = cv2.matchTemplate(img_rgb,template,cv2.TM_CCOEFF_NORMED)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  top_left = max_loc
  bottom_right = (top_left[0] + w, top_left[1] + h)
  cv2.rectangle(img_rgb,top_left, bottom_right, 255, 2)
  cv2.imwrite('image%d-urodz.png' % pageNo, img_rgb)
    
def analyse():
  for i in range(10):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
  lista = list(xrange(1,108))
  lista = lista[:88] + lista[91:]
  for pageNo in lista:
    threadName = "Type-Detection-thread-%d" % pageNo
    item = Item("detect-type", threadName, pageNo, '')
    q.put(item)
  q.join()

analyse()
