#!/usr/bin/env python3

# TODO: Make sure this script works by just double clicking.

import os
import shlex
import subprocess
import time
import urllib.request

albumUrl = "https://photos.app.goo.gl/oSAyRxvCYp8ndDVT7"
photoUrlPrefix = "https://lh3.googleusercontent.com/pw/"
htmlSplit = '"'
suffixDelim = "="
downloadSuffix = "=w1024-h1024-no"
imageExt = ".jpg"

def path(*args):
  return os.path.abspath(os.path.join(*args))

repoDir = path(__file__, "..")
albumDir = path(repoDir, "res/album")
fileListJs = path(repoDir, "lib/albumFiles.js")

def repoRelativePath(f):
  return os.path.relpath(f, start=repoDir)

def run(args):
  result = subprocess.run(
      args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=repoDir,
      text=True)
  if result.returncode != 0:
    print("Command failed: %s" % shlex.join(args))
    print(result.stdout)
    print("Exit code: %s" % result.returncode)
    print()
    exit(1)

def git(*args):
  run(['git', *args])

def getBytes(url):
  retries = 0
  while True:
    try:
      with urllib.request.urlopen(url) as response:
        return response.read()
    except urllib.error.URLError as e:
      retries += 1
      if retries >= 3:
        print("Downloading from URL %s failed:\n%s" % (url, e))
        print()
        exit(1)

def getUtf8(url):
  return getBytes(url).decode("utf-8")

def extractImageUrls(html):
  urls = set()
  for s in html.split(htmlSplit):
    if s.startswith(photoUrlPrefix):
      idx = s.find(suffixDelim)
      if idx >= 0:
        s = s[:idx]
      urls.add(s)
  return urls

def consistentHash(str):
  # 64-bit FNV-1a hash function
  basis = 0xcbf29ce484222325
  prime = 0x100000001b3
  mod = 0x10000000000000000
  h = basis
  for b in str.encode('utf-8'):
    h = ((h * prime)  % mod) ^ b
  return h

class Image:
  def __init__(self, url):
    self.url = url
    self.filename = path(albumDir, hex(consistentHash(url))[2:] + imageExt)

def listDir(d):
  return [path(d, f) for f in os.listdir(d)]

def listFiles(d):
  return [f for f in listDir(d) if os.path.isfile(f)]

def listImages(d):
  return {f for f in listFiles(d) if f.endswith(imageExt)}

def downloadFile(url, filename):
  data = getBytes(url)
  with open(filename, "wb") as file:
    file.write(data)

def generateFileList(fileList, filename):
  with open(filename, "w", encoding="utf-8") as file:
    file.write("""const albumFileList = [
  %s,
];
""" % ',\n  '.join([repr(repoRelativePath(f)) for f in fileList]))

def main():
  print("Downloading updates from GitHub...")
  git("checkout", "main")
  git("fetch", "origin", "main")
  git("reset", "--hard", "origin/main")

  print("Looking for new images on Google photos...")
  allImageUrls = extractImageUrls(getUtf8(albumUrl))
  allImages = [Image(url + downloadSuffix) for url in allImageUrls]
  print("Album contains %s images" % len(allImages))
  allImageFilenames = {img.filename for img in allImages}
  existingImages = listImages(albumDir)
  newImages = [img for img in allImages if img.filename not in existingImages]
  deletableImages = [f for f in existingImages if f not in allImageFilenames]

  msgs = []
  if len(deletableImages) > 0:
    print("Deleting %s removed images" % len(deletableImages))
    msgs.append("Deleted %s" % len(deletableImages))
    for f in deletableImages:
      os.remove(f)

  if len(newImages) > 0:
    msgs.append("Added %s" % len(deletableImages))
  else:
    print("No new images to download")

  if len(msgs) == 0:
    exit(0)
  msgs.append(time.strftime("%Y-%m-%d"))

  print()
  print("Downloading %s new images from Google photos..." % len(newImages))
  for i in range(len(newImages)):
    img = newImages[i]
    print("  Downloading %s of %s: %s" % (i + 1, len(newImages), img.url))
    downloadFile(img.url, img.filename)
  print("Download complete")

  generateFileList([img.filename for img in allImages], fileListJs)

  print()
  print("Uploading updates to GitHub...")
  git('add', fileListJs, *(img.filename for img in newImages), *deletableImages)
  git('commit', '-m', ', '.join(msgs))
  git('push', 'origin', 'main')

  print()
  print("Portfolio updated successfully :)")
  print("The site may take 5-10 minutes to show the changes")

main()
