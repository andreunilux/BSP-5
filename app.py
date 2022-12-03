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




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///videos.db'
db = SQLAlchemy(app)







class Video(db.Model):
    url = db.Column(db.String(200), primary_key=True)
    video_title = db.Column(db.String(200))
    downloaded = db.Column(db.Boolean, nullable=False)
    result = db.Column(db.String(300))
    classified = db.Column(db.Boolean, nullable=False)




@app.route('/')
def homepage():
    return render_template('homepage.html')





@app.route("/check")
def sent_status():
    # get the video id
    url_video = request.args.get("video_id")
    downloading = request.args.get("download_p")
    naming = request.args.get("download_n")
    
    finished = downloading.poll()
    
    if finished is None:
        return render_template('landingpage_download.html',process_download=downloading, process_naming=naming)
    else:
        return render_template('landingpage_classify.html')

    





@app.route("/download", methods=["POST"])
def classify():
    #check if URL
    url_video = request.form.get("url_link_video")
    if not url_video:
        return render_template('400_http.html',status=400)
    
    
    
    #database stuff
    new_video = Video(url=url_video, video_title="", downloaded=False, result="",classified=False)
    db.session.add(new_video)
    db.session.commit()

    
    return redirect(location="http://localhost:8080/downloading?video_id="+ str(url_video))



@app.route("/downloading", methods=["GET"])
def send_video_id():
    query = request.args.to_dict()
    url_video = query.get("video_id") 

    #Hashing video_url



    title = str(".txt")
    name= open(title, "w+")
    
    naming = subprocess.Popen(['youtube-dl '+ url_video+" -e"], shell=True, stdout=name)
    
    
    
    
        
    
    filename = url_video+".log"
    with io.open(filename, "wb") as writer:
        downloading = subprocess.Popen(['youtube-dl '+ url_video], shell=True, stdout=writer)

    return render_template("landingpage_download.html", process_download=downloading, process_naming=naming,  progress=filename, title=title)


if __name__ == "__main__":
    app.run(host='localhost', port=8080,debug=True)


