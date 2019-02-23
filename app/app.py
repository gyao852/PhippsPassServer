from flask import Flask, request, jsonify, render_template
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from queue import Queue
import os
import logging
from flask import send_from_directory
import threading
from marshmallow import fields
import boto3
from flask_wtf import FlaskForm
from wtforms import StringField
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField
import json
import requests
import uuid
import time
import datetime
import subprocess
from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'georgey852@gmail.com'
app.config['MAIL_PASSWORD'] = 'LUfhspvz12!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

# configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] - %(threadName)-10s : %(message)s')

# configure pass folder destination folder
app.config['PASS_FOLDER'] = './Pass Files'

from models import Member, Pass
if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)

# error handlers
@app.errorhandler(404)
def not_found(error):
    logging.debug(request)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

# Index page shows initial dashboard
@app.route("/",methods=['GET'])
def index():
    logging.debug("Index page requested")
    return render_template('index.html')
        # sendMail("gyao@andrew.cmu.edu","some/path.pkpass")



# Member index page shows all members, and
# ability to send emails to users
@app.route("/members",methods=['GET'])
def members():
    logging.debug("Member page requested")
    data = Member.query.order_by(Member.full_name.desc()).all()
    return render_template('tables.html', members = data)


# register user
@app.route('/send_mail',methods=['POST'])
def sendMail():
    print(request.values.get('field', None))
    # return "abc"
    recipient_email = request.values.get('email', None)
    name = request.values.get('name', None)
    logging.debug("send_mail called")
    msg = Message("Digital memberhsip card | Phipps Conservatory and Botanical Gardens",
                  sender="georgeY852@gmail.com",
                  recipients=["mcassidy@phipps.conservatory.org"]) # smoussaw@andrew.cmu.edu
    # msg.body = "some body"
    msg.html = '''
        Dear {},<br><br>
        Phipps Conservatory is always seeking to continue it's
        mission of reducing it's carbon emissions. One of our new initiatives
        is having our membership cards available by phone. Attached to this
        email is your membership card that can be saved and loaded onto your smartphone device.<br><br>
        For Apple devices:
        <ul>
            <li> If you're on your phone, simply double tap on the attached .pkpass file, and it should automatically add
            to your Apple Wallet.<br>
            <li> If you're on your Macbook, you can also double click on the attached file for it to be added to all your Apple devices.
            <br>
            NOTE: This will only work if you've connected your iPhone and Macbook with the same iCloud. If not, you can download your .pkpass
            file, and 'Airdrop' it to your Apple device. Your phone will then automatically add it to Apple Wallet.
        </ul>
        For Android phones:<br>
        <ul>
            <li> Go to the Google Play Store, and install the application 'Passes'<br>
            <li> Double tap on the attached .pkpass file, and then choose to add to 'Passes'<br>
        </ul>
        <br>
        We hope to see you soon!<br><br>
        Mike Cassidy<br>
        Membership Administrator<br>
        412/622-6915, ext. 6500<br>
        mcassidy@phipps.conservatory.org<br>
        <img src='https://i.ibb.co/q5QrGXf/phipps-email-logo.png'><br>
        <font color="#78a22f">Phipps Conservatory and Botanical Gardens</font><br>
        <font color="#78a22f">One Schenley Park</font><br>
        <font color="#78a22f">Pittsburgh, Pa. 15213</font><br>
        <font color="#78a22f"><a href="phipps.conservatory.org"></font><br>
        <font color="#78a22f"><a href="facebook.com/phippsconservatory"></font><br>
        <font color="#78a22f"><a href="twitter.com/phippsnews"></font>
        '''.format(name)
    fileName = "{}.pkpass".format(name.replace(" ", ""))
    with app.open_resource("Pass Files/{}".format(fileName)) as fp:
        msg.attach("{}".format(fileName), "Pass Files/{}".format(fileName), fp.read())
    mail.send(msg)

    #<img src='http://127.0.0.1:5000/static/img/phipps_email_logo.png'><br>
    #
    # member = Member.query.filter_by(full_name=name).first()
    # member_pass = Pass.query.filter_by(member_id=member.id).first()
    # member_pass.last_sent = datetime.datetime.now()
    # db.session.commit()
    logging.debug("mail sent")
    return recipient_email


# Registering a Device to Receive Push Notifications for a Pass
# webServiceURL/version/devices/deviceLibraryIdentifier/registrations/passTypeIdentifier/serialNumber
@app.route("/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership/<serialNumber>", methods=['POST'])
def register_device():
    return

# Getting the Serial Numbers for Passes Associated with a Device
# webServiceURL/version/devices/deviceLibraryIdentifier/registrations/passTypeIdentifier?passesUpdatedSince=tag
@app.route("/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership?passesUpdatedSince=<tag>", methods=['GET'])
def get_serial():
    return

# Getting the Latest Version of a Pass
# webServiceURL/version/passes/passTypeIdentifier/serialNumber
@app.route("/v1/passes/pass.org.conservatory.phipps.membership/<serialNumber>", methods=['GET'])
def get_latest_version():
    return


# Unregistering a Device
# deviceLibraryIdentifier/registrations/passTypeIdentifier/serialNumber
@app.route("/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership/<serialNumber>", methods=['DELETE'])
def unregister_device():
    return

# Logging errors
# webServiceURL/version/log
@app.route("/v1/log", methods=['POST'])
def loggin_error():
    return

# Logic for creating pass
def create_pass():
    # print('pass')
    passFile = "george.pkpass"
    out = subprocess.Popen(['./signpass', '-p', '{}'.format(passFile)],
               stdout=subprocess.PIPE,
               stderr=subprocess.STDOUT)


# configure queue for training models
queue = Queue(maxsize=100)
thread = threading.Thread(target=create_pass, name='PassSignageDaemon')
thread.setDaemon(False)
thread.start()
