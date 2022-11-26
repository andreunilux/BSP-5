#encoding:UTF-8
#Author:André Dussing 
 
"""n application that downloads a publicly available video from a video hosting platform and labels the video using a video classification algorithm."""


from flask import Flask, render_template, request, Response
import os
import hashlib
import time
from flask_sqlalchemy import SQLAlchemy
#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///videos.db'
db = SQLAlchemy(app)

class Video(db.Model):

    hashed_url = db.Column(db.String(200), primary_key=True)
    video_title = db.Column(db.String(200), nullable=False)
    downloaded = db.Column(db.Boolean, nullable=False)
    result = db.Column(db.String(300))
    classified = db.Column(db.Boolean, nullable=False)


@app.route('/')
def homepage():
    return render_template('homepage.html')



@app.route("/download", methods=["POST"])
def classify():
    url_video = request.form.get("url_link_video")
    if not url_video:
        return render_template('400_http.html',status=400)
    
    m = hashlib.sha256()
    m.update(url_video.encode('utf-8'))
    hash = m.hexdigest()
    
    os.system(f'youtube-dl "{url_video}" >"{hash}.log" 2>&1 &')
    #sql stuff
    
    new_video = Video(hashed_url=hash, video_title="", downloaded=False, result="",classified=False)
    db.session.add(new_video)
    db.session.commit()

    log = open(str(hash)+".log", "r")
    print(log.readlines(6))
    print("hey")
    return render_template('landingpage.html', value=log.read())



if __name__ == "__main__":
    app.run(host='localhost', port=8080,debug=True)


