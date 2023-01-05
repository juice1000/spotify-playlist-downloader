from flask import Flask, render_template, request, flash, send_file, url_for, jsonify
import spotify_get_song_names as spt
import youtube_downloader as yt
from config import Prod, Dev
from zipfile import ZipFile
import os
from os.path import basename
from io import BytesIO
import shutil
import time
import spotify_get_song_names as spt
from celery import Celery
import os

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Prod)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/')
def index():
    return render_template('index.html')

def zipping(data, dirName):
    # create a ZipFile object
    with ZipFile(data, 'w') as zipObj:
    # Iterate over all the files in directory
        print('existing in zipping ', os.path.exists(dirName))
        
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                #create complete filepath of file in directory

                filePath = os.path.join(folderName, filename)
                print('filepath to write: ', filePath)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))
        
        
@app.route('/download', methods=('GET', 'POST'))
def download():
    if request.method == 'POST':
        playlist_id = request.json["playlist_id"]
        filetype = request.json["filetype"]
        print(playlist_id)
        if not playlist_id:
            flash('Title is required!')
        # First third of progress bar would be song title retrieval, second third would be download, last would be zipping
        task = background_process.apply_async(args=(playlist_id, filetype))
        result = jsonify({}), 202, {'Location': url_for('progress', task_id=task.id)}
        return result
        

@app.route('/send_zip_file', methods=('GET', 'POST'))
def send_zip_file():
    path = os.path.join(os.getcwd(), 'static', 'music_files')
    data = BytesIO()
    print('existing before zipping ', os.path.exists(path))
    zipping(data, path)
    data.seek(0)
    print('existing after seek ', os.path.exists(path))
    shutil.rmtree(path, ignore_errors=False, onerror=None)
    return send_file(data, mimetype='application/zip', as_attachment=True, download_name='music_playlist.zip')


@celery.task(bind=True)
def background_process(self, playlist_link, filetype):
    process = 0
    song_titles = spt.track_data_extractor(playlist_link)
    process = 30
    single_song_percent = int(60 / len(song_titles))
    self.update_state(state='PROGRESS', meta={'current': process, 'total': 100, 'status': 'downloading songs'})

    for song in song_titles:
        yt.download_from_link(song, filetype)
        process += single_song_percent
        self.update_state(state='PROGRESS', meta={'current': process, 'total': 100, 'status': 'downloading songs'})

    self.update_state(state='PROGRESS', meta={'current': 95, 'total': 100, 'status': 'finished downloading songs', 'intermediate_result': 42})
    time.sleep(2)

    path = os.path.join(os.getcwd(), 'static', 'music_files')
    print('path still existing: ', os.path.exists(path))
    while os.path.exists(path):
        print ('waiting for files to be downloaded')

    print('files successfully downloaded')
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route('/progress/<task_id>', methods=('GET', 'POST'))
def progress(task_id):
    task = background_process.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Scanning through playlist...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    json_response = jsonify(response)
    return json_response


if __name__ == "__main__":
    app.run(host=app.config.get("DOMAIN"))
