from flask import Flask, request, jsonify, send_from_directory, Response
from config import Config as SETTING
from flask_pymongo import pymongo
import os
import json


app = Flask(__name__)
app.secret_key = SETTING.FLASK_KEY


# Get Data from Database
myclient = pymongo.MongoClient(SETTING.MONGO_LINK)
GMusicDatabase = myclient["GMusicDatabase"]
GMusicDatabaseCollection = GMusicDatabase["GMusicDatabaseData"]


@app.route('/', methods=['GET'])
def index():
    try:
        GMusicList = GMusicDatabaseCollection.find({}, {'_id': False})
        # Convert Data into List
        GMusicFetchData = []
        for GMusic in GMusicList:
            GMusicFetchData.append(GMusic)
        response = Response(json.dumps(GMusicFetchData), status=200, mimetype='application/json')
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        print(e)
        response = Response(json.dumps({"status" : False, "message" : "Error"}), status=404, mimetype='application/json')
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/addMusic', methods=['POST'])
def addMusicFunc():
    if request.method == 'POST' and request.form.get('auth') == SETTING.AUTH:
        try:
            newData = {
                "spotify_id": request.form.get('spotify_id'),
                "album": request.form.get('album'),
                "artist": request.form.get('artist').split(','),
                # "duration": int(request.form.get('duration')),
                # "lyrics": request.form.get('lyrics'),
                "name": request.form.get('name'),
                "music": request.form.get('music'),
                "poster": request.form.get('poster'),
            }
            MusicID = GMusicDatabaseCollection.insert_one(newData).inserted_id
            # GMusicDatabaseCollection.update_one({'_id': MusicID}, {'$set': {'music': str(MusicID), 'poster': str(MusicID), 'lyrics':str(MusicID)}})
            response = Response(json.dumps({"status": True, "id": str(MusicID), "message": "New Song has been added"}), status=200, mimetype='application/json')
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except:
            response = Response(json.dumps({"status": False, "message": "Error while adding data"}), status=500, mimetype='application/json')
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    else:
        response = Response(json.dumps({"status": False, "message": "You are not authenticated"}), status=401, mimetype='application/json')
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/deleteMusic', methods=['POST'])
def deleteMusic():
    if request.method == 'POST' and request.form.get('auth') == SETTING.AUTH:
        try:
            print(request.form.get('doc_id'))
            GMusicDatabaseCollection.delete_one({"music" : request.form.get('doc_id')})
            response = Response(json.dumps({"status": True, "message": "Music Successfully Deleted"}), status=200, mimetype='application/json')
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except:
            response = Response(json.dumps({"status": False, "message": "Not able to delete"}), status=500, mimetype='application/json')
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response


@app.route('/check', methods=['POST'])
def checkMusic():
    if request.method == 'POST' and request.form.get('auth') == SETTING.AUTH:
        try:
            print(request.form.get('spotify_id'))
            if request.form.get('spotify_id') != None:
                GMusicCheck = GMusicDatabaseCollection.count_documents({"spotify_id" : request.form.get('spotify_id')})
                if GMusicCheck == 0:
                    response = Response(json.dumps({"status": True, "message": "Music Not Available"}), status=404, mimetype='application/json')
                else:
                    response = Response(json.dumps({"status": True, "message": "Music Available"}), status=200, mimetype='application/json')
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                response = Response(json.dumps({"status": False, "message": "Invalid Music ID"}), status=500, mimetype='application/json')
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
        except:
            response = Response(json.dumps({"status": False, "message": "Not able to delete"}), status=500, mimetype='application/json')
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/x-icon')


if __name__ == "__main__":
    app.run(debug=True)