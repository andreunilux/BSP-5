#encoding:UTF-8
#Author:André Dussing 
 
"""n application that downloads a publicly available video from a video hosting platform and labels the video using a video classification algorithm."""


from flask import Flask, render_template, request, Response, redirect
import os
import hashlib
import subprocess
import ctypes
import json

#DATABSE
from sqlalchemy import create_engine, PrimaryKeyConstraint, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker




app = Flask(__name__)
Base = declarative_base()

class Video(Base):
    __tablename__ = "video"

    hash = Column("hash",String, primary_key=True)
    url = Column("url",String)
    video_title = Column("video title",String)
    downloaded = Column("downloaded",Boolean, nullable=False)
    result = Column("results",String)
    classified = Column("classified", Boolean, nullable=False)

    def __init__(self, hash, url, video_title, downloaded, result, classified):
        self.hash = hash
        self.url = url
        self.video_title = video_title
        self.downloaded = downloaded
        self.result = result
        self.classified = classified

    def __repr__(self) -> str:
        return f"\"hash\":\"{self.hash}\",\"url\":\"{self.url}\", \"video_title\":\"{self.video_title}\", \"downloaded\":\"{self.downloaded}\", \"results\":\"{self.result}\", \"classified\":\"{self.classified}\""


#Database intilization 
engine = create_engine("sqlite:///videos.db")
#create the tables
Base.metadata.create_all(bind=engine)
Session= sessionmaker(bind=engine)
session = Session()





@app.route('/')
def homepage():
    return render_template('homepage.html')



@app.route("/download", methods=["POST"])
def download():
    #check if URL
    video_url = request.form.get("url_link_video")
    if not video_url:
        return render_template('400_http.html',status=400)
    
    #Hashing video_url
    m = hashlib.sha256()
    m.update(video_url.encode('utf-8'))
    hash = m.hexdigest()
    
    exists = session.query(Video).filter(Video.hash ==hash).first()
    if (bool(exists)):
        if exists.classified==True:
            return render_template("result.html", result_classes=str(exists.result))
        else:
            return redirect(location="http://localhost:8080/classify?video_id="+ str(hash),code=302)


    #create new video
    new_video = Video(hash=hash, url=video_url, video_title="", downloaded=False, result="",classified=False)
    session.add(new_video)
    session.commit()

    render_template("landingpage_download.html")
    return redirect(location="http://localhost:8080/downloading?video_id="+ str(hash),code=302)



@app.route("/downloading", methods=["GET"])
def send_video_id():
    query = request.args.to_dict()
    hash = str(query.get("video_id")) 
    
    #Query to get video url equal to the hash
    current_video = session.query(Video).filter(Video.hash == hash).first()
    video_json = "{"+str(current_video)+"}"
    video_dict = json.loads(video_json)
    video_url = video_dict.get("url")
    

    #getting video name with yt-dl
    title = str('/home/student/Flask/logfiles/'+hash+"_name.txt")
    name= open(title, "w+")
    naming = subprocess.Popen(['youtube-dl '+ video_url +" -e"], shell=True, stdout=name)
    
    #downloading video with yt-dl
    filename = '/home/student/Flask/logfiles/'+hash+"_progress.log"
    writer= open(filename, "w+")
    downloading = subprocess.Popen(['youtube-dl -o "%(title)s.%(ext)s" '+ video_url+ ' --merge-output-format mp4'], shell=True, stdout=writer)

    return render_template("landingpage_download.html", process_download=id(downloading), process_naming=id(naming))



@app.route("/check_download", methods=['POST'])
def sent_status_d():
    if request.method == 'POST':
        #JSON request contains video_url(id),download process, and naming process  
        data_json = request.get_json()
        hash = data_json['id']
        downloading = ctypes.cast(int(data_json['process_id_d']), ctypes.py_object).value
        naming = ctypes.cast(int(data_json['process_id_n']), ctypes.py_object).value
    
        finished = downloading.poll()
        
        if finished is None:
            return "-1"
        elif finished ==0:
            #set video in video to downloaded true and assign name to the video
            current_video = session.query(Video).filter(Video.hash == hash).first()
            with open('/home/student/Flask/logfiles/'+hash+"_name.txt", 'r') as file:
                data = file.read()
                current_video.video_title = data
                current_video.downloaded = True
            session.commit()
            return hash
            


@app.route("/classify", methods=["GET"])
def  classify():
    query = request.args.to_dict()
    hash = str(query.get("video_id")) 
    # get current file name of the video
    current_video = session.query(Video).filter(Video.hash == hash).first()
    video_title_str = str(current_video.video_title)
    title = video_title_str.strip()+".mp4"
    
    filename = '/home/student/Flask/logfiles/'+hash+"_classify.text"
    writer= open(filename, "w+")
    classification  = subprocess.Popen(["python","kinetics400_demo_video.py",title], stdout=writer)

    return render_template("landingpage_classify.html", process_classify=id(classification))


@app.route("/check_classify", methods=['POST'])
def sent_status_c():
    if request.method == 'POST':
        #JSON request contains hash and classification process
        data_json = request.get_json()
        hash = data_json['id']
        classification = ctypes.cast(int(data_json['process_id_c']), ctypes.py_object).value
    
        finished = classification.poll()
        
        if finished is None:
            return "-1"
        elif finished ==0:
            #set video in video to classified true and asssign result to video
            current_video = session.query(Video).filter(Video.hash == hash).first()
            with open('/home/student/Flask/logfiles/'+hash+"_classify.text", 'r') as file:
                data = file.readlines()[-1]
                current_video.result = data
                current_video.classified = True
            session.commit()
            return hash



@app.route("/result", methods=["GET"])
def  result():
    query = request.args.to_dict()
    hash = str(query.get("video_id")) 
    # get current file name of the video
    current_video = session.query(Video).filter(Video.hash == hash).first()
    video_class = str(current_video.result)
    session.commit()
    session.flush()
    return render_template("result.html", result_classes=video_class)


if __name__ == "__main__":
    app.run(host='localhost', port=8080,debug=True)


