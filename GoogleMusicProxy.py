#! /usr/bin/env python
# -*- coding: utf-8 -*-

# GoogleMusicProxy.py
#
# Copyright (C) 2010 - xulong <fangkailove@gmail.com>
#

import BaseHTTPServer, SocketServer, urllib, urllib2, urlparse
import re
import hashlib
import math
import traceback
import webbrowser
import rhythmdb
import string
from xml.dom.minidom import parse, parseString ,Document 
import xml
import os
import re
import gtk

_storefile = os.path.expanduser('~/gmusiclist.xml')

#def msg(txt):
#   f = open("/home/gnolux/Desktop/dbg.txt",'w')
#   f.write(txt)
#   f.close()

global bs
class  GoogleMusicProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
       
    def do_GET(self):
        # path check

        print "Request path:",self.path 
        (scm, netloc, path, params, query, _) = urlparse.urlparse(self.path)
        print "remove http and param , path:",path
        if path.startswith('/music/addmusic'):
            #Get Music ID
            self.path=urllib.unquote(self.path)
            self.path=self.path.replace("?q=http://www.google.cn/music/top100/player_iframe","")
            #self.wfile.write(self.path)
            self.path=self.path[self.path.find('=')+1:self.path.find('&')]
            id = self.path

            getSongsInfo(id)
            
            #ary = self.path.split(',')
            #for id in ary:
            #    print id
            #    getSongsInfo(id)
            #    print bs

            #add javascript to page for close current webpage
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.end_headers()

            self.wfile.write("<html><body><script language='javascript'>window.close();</script></bod></html>")
            self.connection.close()
            return

        # coding-hard to google.cn
        scm = "http"
        netloc = "www.google.cn"

        # create new path
        path = urlparse.urlunparse((scm, netloc, path, params, query, ''))
        try:
            resp = urllib2.urlopen(path)
            # write hello

            self.send_response(resp.code)
            # write headers
            for line in resp.info().headers:
                if line != '':
                    (name, _, value) = line.partition(':')
                    name = name.strip()
                    value = value.strip()
                    self.send_header(name, value)
            self.end_headers()
            # write page
            data = resp.read()
            #if resp.headers["content-type"].startswith("text/html"):
            if resp.headers["content-type"].startswith("text/javascript"):
                # replace  html code to catch "add muisc" requests

                data=re.compile(".onclickStreaming=function.*\n" ).sub(".onclickStreaming=function(a){a=a.substring(a.indexOf('?'));a='./addmusic'+a;window.open(a);return 1};",data )

                #data=data.replace("t.onclickStreaming=function(a){function c(){if(!t.checkIsLoading()){window.clearInterval(d);t.Ll(a)}}if(t.isPlayerLoading)return k;t.isPlayerLoading=h;t.playerPageTarget=s.popupBlockerDetection.openWindowWithMessageIfBlocked(a,t.ONLINE_PLAYER_SINGLETON_NAME,t.PLAYER_POPUP_FEATURE);t.toggleCursorStyle(h);var d=window.setInterval(c,300);t.playerPageTarget.focus();return k};","t.onclickStreaming=function(a){a=a.substring(a.indexOf('?'));a='./addmusic'+a;window.open(a);return 1};" )

                #data=data.replace("_sl_addSongsToPlaylist(&quot;&quot;, &quot;http://www.google.cn/music/top100/player_iframe&quot;",\
                        #        "_sl_addSongsToPlaylist(&quot;&quot;, &quot;addmusic&quot;")
                #data=data.replace("/music/url?q\\x3dhttp%3A%2F%2Fwww.google.cn%2Fmusic%2Ftop100%2Fplayer_iframe%3Fid%3D","addmusic?id=")

            self.wfile.write(data)
        finally:
            self.connection.close()


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): 
    pass

def main():
    httpd = ThreadingHTTPServer(('127.0.0.1', 8000), GoogleMusicProxyHandler )
    webbrowser.open_new("http://localhost:8000/music/homepage")
    httpd.serve_forever()


def getSongUrl(id):
    GOOGLE_PLAYER_KEY = "ecb5abdc586962a6521ffb54d9d731a0"
    hash = hashlib.md5(GOOGLE_PLAYER_KEY + id).hexdigest()
    url="http://www.google.cn/music/songstreaming?id=" + id + "&output=xml&sig=" + hash
    resp2=urllib2.urlopen(url)
    xmlCont2=resp2.read()
    dom2=parseString(xmlCont2)
    url = dom2.getElementsByTagName('songUrl')[0].childNodes[0].nodeValue
    return url

def getSongsInfo(ids):
    #http://www.google.cn/music/song?id=S29859666b83d9b88,S6ff6c27f4a60ddfd,S51fc55d7512c0dbf&output=xml
    GOOGLE_PLAYER_KEY = "ecb5abdc586962a6521ffb54d9d731a0"
    url = "http://www.google.cn/music/song?id=" + ids + "&output=xml"
    resp = urllib2.urlopen(url)
    xmlCont = resp.read()
    dom1=parseString(xmlCont)
    elements=dom1.getElementsByTagName('song')
    songs = []
    for element in elements:
          name="" 
          artist="" 
          album="" 
          duration=0 
          genre=""
          location=""
          comment=""
          try:
              id=element.getElementsByTagName('id')[0].childNodes[0].nodeValue
              comment=id              
              name=element.getElementsByTagName('name')[0].childNodes[0].nodeValue
              artist=element.getElementsByTagName('artist')[0].childNodes[0].nodeValue
              album=element.getElementsByTagName('album')[0].childNodes[0].nodeValue
              durationf=float(element.getElementsByTagName('duration')[0].childNodes[0].nodeValue)
              duration=int(math.ceil(durationf))
              hash = hashlib.md5(GOOGLE_PLAYER_KEY + id).hexdigest()
              url="http://www.google.cn/music/songstreaming?id=" + id + "&output=xml&sig=" + hash
              resp2=urllib2.urlopen(url)
              xmlCont2=resp2.read()
              dom2=parseString(xmlCont2)
              #url = dom2.getElementsByTagName('songUrl')[0].childNodes[0].nodeValue
              genre =  dom2.getElementsByTagName('genre')[0].childNodes[0].nodeValue
              location= getSongUrl(comment)
          except:
              print 'xml error'


          try:
              print "print bs"

              entry = bs.db.entry_new(bs.entry_type, id)
              bs.db.set(entry, rhythmdb.PROP_COMMENT, comment)
              bs.db.set(entry, rhythmdb.PROP_LOCATION, location)
              bs.db.set(entry, rhythmdb.PROP_TITLE, name)
              bs.db.set(entry, rhythmdb.PROP_ARTIST, artist)
              bs.db.set(entry, rhythmdb.PROP_ALBUM, album)
              bs.db.set(entry, rhythmdb.PROP_DURATION, duration)
              ##bs.db.set(entry, rhythmdb.PROP_TRACK_NUMBER, song['track_number'])
              bs.db.set(entry, rhythmdb.PROP_GENRE, genre)
              

              bs.db.commit()       
          except:
              continue

          doc = Document()
          songlist = doc.createElement("songlist")
          doc.appendChild(songlist) 
          #appendNode(doc,id,comment,name,artist,album,str(duration),genre)
          saveList(doc)
    #return songs

def appendNode(doc,id,comment,name,artist,album,duration,genre):
    n_songlist = doc.getElementsByTagName('songlist')[0]
    n_song = doc.createElement("song")
    n_songlist.appendChild(n_song)

    n = doc.createElement("id")
    n_song.appendChild(n)
    n_text = doc.createTextNode(id)
    n.appendChild(n_text)

    n = doc.createElement("comment")
    n_song.appendChild(n)
    n_text = doc.createTextNode(comment)
    n.appendChild(n_text)

    n = doc.createElement("name")
    n_song.appendChild(n)
    n_text = doc.createTextNode(name)
    n.appendChild(n_text)


    n = doc.createElement("artist")
    n_song.appendChild(n)
    n_text = doc.createTextNode(artist)
    n.appendChild(n_text)

    n = doc.createElement("album")
    n_song.appendChild(n)
    n_text = doc.createTextNode(album)
    n.appendChild(n_text)

    n = doc.createElement("duration")
    n_song.appendChild(n)
    n_text = doc.createTextNode(duration)
    n.appendChild(n_text)

    n = doc.createElement("genre")
    n_song.appendChild(n)
    n_text = doc.createTextNode(genre)
    n.appendChild(n_text)



def saveList(doc=None):


    f = open(_storefile, 'w')

    if doc==None:
        doc = Document()
        songlist = doc.createElement("songlist")
        doc.appendChild(songlist)


    for row in bs.props.query_model:
        entry = row[0]
        id=bs.db.entry_get(entry, rhythmdb.PROP_LOCATION)
        comment=bs.db.entry_get(entry, rhythmdb.PROP_COMMENT)
        name=bs.db.entry_get(entry, rhythmdb.PROP_TITLE)
        artist=bs.db.entry_get(entry, rhythmdb.PROP_ARTIST)
        album=bs.db.entry_get(entry, rhythmdb.PROP_ALBUM)
        duration=str(bs.db.entry_get(entry, rhythmdb.PROP_DURATION))
        genre=bs.db.entry_get(entry, rhythmdb.PROP_GENRE)



        appendNode(doc,id,comment,name,artist,album,duration,genre)


    f.write(doc.toxml())
    f.close()

def loadList():
    if os.path.isfile(_storefile):
        f = open(_storefile, 'r')
        xmlCont = f.read()
        try:
            dom1=parseString(xmlCont)
        except:
            return

        

        elements=dom1.getElementsByTagName('song')
        for element in elements:
            try:
               
                name="" 
                artist="" 
                album="" 
                duration=0 
                genre=""
                id=element.getElementsByTagName('id')[0].childNodes[0].nodeValue
                comment =  element.getElementsByTagName('comment')[0].childNodes[0].nodeValue
                name=element.getElementsByTagName('name')[0].childNodes[0].nodeValue
                artist=element.getElementsByTagName('artist')[0].childNodes[0].nodeValue
                album=element.getElementsByTagName('album')[0].childNodes[0].nodeValue
                duration=int(element.getElementsByTagName('duration')[0].childNodes[0].nodeValue)
                genre =  element.getElementsByTagName('genre')[0].childNodes[0].nodeValue
                location= getSongUrl(comment)

                
            except:
              print 'xml error'
              

            try:
                entry = bs.db.entry_new(bs.entry_type, id)
                bs.db.set(entry, rhythmdb.PROP_COMMENT, comment)
                bs.db.set(entry, rhythmdb.PROP_LOCATION, location)
                bs.db.set(entry, rhythmdb.PROP_TITLE, name)
                bs.db.set(entry, rhythmdb.PROP_ARTIST, artist)
                bs.db.set(entry, rhythmdb.PROP_ALBUM, album)
                bs.db.set(entry, rhythmdb.PROP_DURATION, duration)
                #bs.db.set(entry, rhythmdb.PROP_TRACK_NUMBER, song['track_number'])
                bs.db.set(entry, rhythmdb.PROP_GENRE, genre)
                  
                bs.db.commit()       
            except:
                continue
        f.close() 



if __name__ == '__main__':
    main()





