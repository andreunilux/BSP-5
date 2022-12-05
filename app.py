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
import ctypes



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





@app.route("/check", methods=['POST'])
def sent_status():
    if request.method == 'POST':
        #JSON request contains video_url(id),download process, and naming process  
        data_json = request.get_json()
        video_url = data_json['id']
        downloading = ctypes.cast(int(data_json['process_id_d']), ctypes.py_object).value
        naming = ctypes.cast(int(data_json['process_id_n']), ctypes.py_object).value
        
        print(downloading.poll())  
        finished = downloading.poll()
        
        if finished is None:
            #set video in video to downlowd true
            print("video download not finished")
            return -1
        elif finished ==0:
            return video_url
            




    

@app.route("/classify", methods=["GET"])
def  classify():
    query = request.args.to_dict()
    video_url = str(query.get("video_id")) 
    return render_template("landingpage_classify.html") 




@app.route("/download", methods=["POST"])
def download():
    #check if URL
    video_url = request.form.get("url_link_video")
    if not video_url:
        return render_template('400_http.html',status=400)
    
    #
    
    #database stuff
    new_video = Video(url=video_url, video_title="", downloaded=False, result="",classified=False)
    db.session.add(new_video)
    db.session.commit()

    render_template("landingpage_download.html")
    return redirect(location="http://localhost:8080/downloading?video_id="+ str(video_url),code=302)



@app.route("/downloading", methods=["GET"])
def send_video_id():
    query = request.args.to_dict()
    video_url = str(query.get("video_id")) 
    video_url1 = str(query.get("video_id")) 

    #Hashing video_url
    m = hashlib.sha256()
    m.update(video_url.encode('utf-8'))
    hash = m.hexdigest()
    print(video_url)
    #getting video name with yt-dl
    title = str('/home/student/Logs/'+hash+"_name.txt")
    name= open(title, "w+")
    naming = subprocess.Popen(['youtube-dl '+ video_url1 +" -e"], shell=True, stdout=name)
    
    #downloading video with yt-dl
    filename = '/home/student/Logs/'+hash+"_progress.log"
    writer= open(filename, "w+")
    downloading = subprocess.Popen(['youtube-dl '+ video_url1], shell=True, stdout=writer)

    return render_template("landingpage_download.html", process_download=id(downloading), process_naming=id(naming))






if __name__ == "__main__":
    app.run(host='localhost', port=8080,debug=True)


