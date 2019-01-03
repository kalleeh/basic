import boto3
from botocore.exceptions import ValidationError, ClientError
import logging
import uuid
import json
from flask import Flask, render_template

client = boto3.client('s3')


def create_temp_file(size, file_name, file_content):
    random_file_name = ''.join([str(uuid.uuid4().hex[:6]), file_name])
    with open(random_file_name, 'w') as f:
        f.write(str(file_content) * size)
    return random_file_name


app = Flask(__name__)


if __name__ != ‘__main__’:
    gunicorn_logger = logging.getLogger(‘gunicorn.error’)
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    
@app.route('/health')
def health():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  

@app.route('/')
@app.route('/index')
def index():
    posts = []
    user = {'username': 'Karl'}

    first_file_name = create_temp_file(300, 'firstfile.txt', 'f')

    try:
        # upload file to your bucket
        client.upload_file(Filename=first_file_name, Bucket='mys3-s3bucket-3alkllybxdoy', Key=first_file_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExistsException':
            app.logger.error('AlreadyExistsException: {}'.format(e))
            posts.append({
                'author': {'username': 'Server'},
                'body': 'Unknown Exception {}'.format(e.text)
            })
        else:
            app.logger.error('Unexpected Error: {}'.format(e))
            posts.append({
                'author': {'username': 'Server'},
                'body': 'Unexpected Error: {}'.format(e.text)
            })
    except Exception as e:
        app.logger.error('Unexpected Error: {}'.format(e))
        posts.append({
            'author': {'username': 'Server'},
            'body': 'Unexpected Error: {}'.format(e)
        })
    else:
        app.logger.info('Successfully wrote file: {}'.format(first_file_name))
        posts.append({
            'author': {'username': 'Karl'},
            'body': 'I just wrote a new file named: {}'.format(first_file_name)
        })

    return render_template('index.html', title='Home', user=user, posts=posts)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)