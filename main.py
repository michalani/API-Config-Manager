import markdown
import flask
from flask import Flask, request, jsonify,flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import markdown.extensions.fenced_code
import os
import hashlib
import subprocess
import time
import requests
from pygments.formatters import HtmlFormatter
from flaskext.markdown import Markdown

#Markdown(app)
ALLOWED_EXTENSIONS = {'txt', 'config'}

app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.config['FOLDER_CONFIGS'] = 'configs'


@app.route('/api/v1/c/', methods=['GET'])
def configs():
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):
                return jsonify(os.listdir('configs/'))
    else:
        return jsonify("No license detected")

@app.route('/api/v1/c/<config>')
def configs_by_name(config):
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):
            return directory_by_name(config,'configs/')
    else:
        return jsonify("No license detected")


@app.route('/api/v1/up/c/',methods=['GET','POST'])
def add_config():
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):
            return upload_file(app.config['FOLDER_CONFIGS'])
    else:
        return jsonify("No license detected")

@app.route('/api/v1/dl/c/<config>', methods=['GET'])
def download_config(config):
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):
            return download(config,app.config['FOLDER_CONFIGS'])
    else:
        return jsonify("No license detected")

@app.route('/api/v1/rm/c/<config>', methods=['GET'])
def remove_config(config):
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):
            return remove(config,app.config['FOLDER_CONFIGS'])
    else:
        return jsonify("No license detected")

def remove(item,directory):
    dir_list = os.listdir(directory)
    for i in dir_list:
        if item == i:
            path = os.path.join(directory,item)
            os.remove(path)
            return jsonify("200 - File has been removed!")
    return jsonify("404 - File not found!")

def download(item,directory):
    dir_list = os.listdir(directory)
    for i in dir_list:
        if item == i:
            return send_from_directory(directory=directory, filename=item,as_attachment=True)
    return jsonify("404 - File not found!")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#@app.route('/up', methods=['GET', 'POST'])
def upload_file(folderName):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folderName, filename))
            return jsonify("File uploaded to folder "+folderName)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def directory_by_name(item,directory):
    dir_list = os.listdir(directory)
    for i in dir_list:
        if item == i:
            sha256_hash = hashlib.sha256()
            with open(directory+item,"rb") as f:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(byte_block)
                hash = (sha256_hash.hexdigest())
                results = [{'sha256_hash': hash,'filename': item}]
            break
        else:
            results = "404 - File not found!"
    return jsonify(results)


@app.route('/api/v1/run/')
def open_bullet():
    if 'license' in request.args:
        if(isValidLicense(request.args['license']) == 1):                
            cmd = ['./calc.exe']
            p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            stdout,stderr = p.communicate()
            #outputfinal = stdout.decode("utf-8").replace('\r\n','\r')
            outputfinal = ((stdout).decode("utf-8"))
            notify(outputfinal)
            return jsonify(outputfinal)
    else:
        return jsonify("No license detected")

def isArgument(argumentStr):
    if argumentStr in request.args:
        return True

#@app.route('/api/v1/notif/<msg>')
def notify(msg):
    url = "https://discordapp.com/api/webhooks/710572272112631869/m-BtfENjeeoB3GwHeYbIXQfx4PUNDbb9FKaNtr5SCtnTjlMWYusAcwjgTidddO3PM24j"
    username = "tester"
    return jsonify(sendMsg(msg,username,url))

def sendMsg(message,username,url):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {"username": ""+username+"", "content": ""+message+""}
    r = requests.post(url, json=data, headers=headers)
    if(r.status_code > 199 and r.status_code < 300):
        return ("Notification -  Successfully sent")
    else:
        return ("Notification - Something went wrong!")

def isValidLicense(user_license):
    license = open("license.txt", "r+").read()
    if(license == user_license):
        return 1
    else:
        return 0

app.run()
#app.run(host="0.0.0.0", port="56032")
