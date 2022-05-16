from flask import render_template, request, Blueprint, jsonify, redirect, url_for, session, g
from app.api_call_pred import api_call

import datetime
import json
import traceback
import pandas as pd
from io import TextIOWrapper
from csv import writer
import os
import pickle




main = Blueprint('main', __name__)


@main.before_request
def before_request():
    g.admin = None
    g.upload = None
    if 'admin' in session:
        g.admin = session['admin']
    if 'upload' in session:
        g.upload = session['upload']


# Login page


@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session.pop('admin', None)
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['admin'] = 'admin'
            return redirect(url_for('main.home'))
    return render_template('login.html', error=error)
# user Page


@main.route("/")
def user():
    return render_template('index.html')
# Admin page

@main.route("/home")
def home():
    if not g.admin:
        return redirect(url_for('main.login'))
    else:
        return render_template('admin.html')


@main.route("/exploration")
def exploration():
    if not g.admin:
        return redirect(url_for('main.login'))
    else:
        return render_template('exploration.html')


@main.route("/interaction")
def interaction():
    return render_template('interaction.html')

@main.route("/dataentry", methods=['GET', 'POST'])
def dataentry():
    success =  None
    if request.method == 'POST':
        content = request.form.to_dict().values()
        print((content))
        
        with open('./app/UPLOAD_FOLDER/only_accident_points.csv', 'a', newline='') as f_object:    
            writer_object = writer(f_object)
            writer_object.writerow(content)  
            f_object.close()
        success = 'Data is uploaded.'
        return render_template('dataentry.html', success=success)
        
    else :
        return render_template('dataentry.html')

@main.route("/dataset")
def dataset():
    if not g.admin:
        return redirect(url_for('main.login'))
    else:
        return render_template('dataset.html')


@main.route("/map")
def map():
    return render_template('predictionmap.html')


@main.route("/month")
def month():
    return render_template('1month.html')


@main.route("/hour")
def hour():
    return render_template('2hour.html')


@main.route("/vehicles")
def vehicles():
    return render_template('3vehicles.html')


@main.route("/casualties")
def casualties():
    return render_template('4casualties.html')


@main.route("/boroughs")
def boroughs():
    return render_template('5boroughs.html')


@main.route("/london")
def london():
    return render_template('6london.html')
            
@main.route('/upload', methods=['GET', 'POST'])
def upload():

    if not g.admin:
        return redirect(url_for('main.login'))
    else:
        # this will work when file is not uploaded else it will redirect to /uploaded
        if not g.upload:
            success = None
            if request.method == 'POST':
                f = request.files['file']
                existing_file=pd.read_csv("./app/UPLOAD_FOLDER/only_accident_points.csv")
                name="only_accident_points.csv"
                existing_file=existing_file.append(pd.read_csv(f),ignore_index=True)
                existing_file.to_csv("./app/UPLOAD_FOLDER/only_accident_points.csv",index=False)
                csv_file=pd.read_csv("./app/UPLOAD_FOLDER/"+name)

                success = 'Success: File is uploaded.'

                session['upload'] = 'upload'
                return render_template('upload.html', success=success)
                # return render_template('uploaded.html')


            session['upload'] = None

            return render_template('upload.html')
        else:
            session['upload'] = 'upload'
            return render_template('alreadyuploaded.html')


# API to get user inputs
@main.route('/prediction', methods=['POST'])
def prediction():
    try:
        req_data = request.get_json()
        origin = req_data['origin']
        destination = req_data['destination']
        date_time = req_data['datetime']

        # process time
        tm = datetime.datetime.strptime(
            date_time, '%Y/%m/%d %H:%M').strftime('%Y-%m-%dT%H:%M')

        out = api_call(origin, destination, tm)

        return json.dumps(out)

    except:
        return jsonify({'trace': traceback.format_exc()})


@main.route('/uploaded')
def uploaded():
    if not g.admin:
        return redirect(url_for('main.login'))
    else:
        data = pd.read_csv("./app/UPLOAD_FOLDER/only_accident_points.csv")
        return render_template('uploaded.html', tables=[data.to_html()])


@main.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('admin', None)
    session.pop('upload', None)
    return render_template('logout.html')
