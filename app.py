#encoding:UTF-8
#Author:André Dussing 
 
"""n application that downloads a publicly available video from a video hosting platform and labels the video using a video classification algorithm."""


from flask import Flask, render_template, request, Response, redirect
import os
import hashlib
from flask_sqlalchemy import SQLAlchemy
import sys
import time
import re
import subprocess
import logging
import io



#Ask for thread save data structure

data=[]



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///videos.db'
db = SQLAlchemy(app)







class Video(db.Model):
    hashed_url = db.Column(db.String(200), primary_key=True)
    video_title = db.Column(db.String(200))
    downloaded = db.Column(db.Boolean, nullable=False)
    result = db.Column(db.String(300))
    classified = db.Column(db.Boolean, nullable=False)




@app.route('/')
def homepage():
    return render_template('homepage.html')





@app.route("/check")
def sent_status():
    hash = request.args.get("video_id")
    #logfile = open(data[0], "r")
    #last_line = logfile.readline(3)
    #progress = re.search("d{1}\.d{1}%",last_line)
    return render_template('landingpage.html', value='f')

    if data[2].poll() != None:
        with open(data[1], "r") as f:
            title_db = f.readline(1)
            

    return render_template('landingpage2.html')
    





@app.route("/download", methods=["POST"])
def classify():
    #check if URL
    url_video = request.form.get("url_link_video")
    if not url_video:
        return render_template('400_http.html',status=400)
    
    #create Hash
    m = hashlib.sha256()
    m.update(url_video.encode('utf-8'))
    hash = m.hexdigest()
    
    title = "title"+hash+".txt"
    with io.open(title, "w") as name:
        naming = subprocess.Popen(['youtube-dl '+ url_video+" -e"], shell=True, stdout=name)
    
        
    
    filename = hash+".log"
    with io.open(filename, "w") as writer:
        downloading = subprocess.Popen(['youtube-dl '+ url_video], shell=True, stdout=writer)
       


    #database stuff
    new_video = Video(hashed_url=hash, video_title="", downloaded=False, result="",classified=False)
    db.session.add(new_video)
    db.session.commit()

    #store 
    data.append(filename)
    data.append(title)
    data.append(naming)
    data.append(downloading)
    
    return redirect("landingpage.html?videoid="+hash)

    
    


if __name__ == "__main__":
    app.run(host='localhost', port=8080,debug=True)


