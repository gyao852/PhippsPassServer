import os
import logging
import threading
from flask import Flask, request, jsonify, render_template
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from queue import Queue
from flask_mail import Mail
from flask_mail import Message
import json
import datetime


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['SERVER_EMAIL']
app.config['MAIL_PASSWORD'] = os.environ['SERVER_EMAIL_PASSWORD']
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

from models import Member, Card, Device, member_card_association, registration

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)


# error handlers
@app.errorhandler(404)
def not_found(error):
    logging.debug(request)
    logging.debug(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    logging.debug(error)
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(401)
def not_authorized(error):
    logging.debug(error)
    return make_response(jsonify({'error': 'Unauthorized'}), 401)


# Index page shows initial dashboard
@app.route("/", methods=['GET'])
@app.route("/index.html", methods=['GET'])
def index():
    logging.debug("Index page requested")
    members = Member.query.all()
    passes = Card.query.all()
    devices = Device.query.all()
    return render_template('index.html', memberCnt=len(members), passCnt=len(passes), deviceCnt=len(devices), pendingCnt=0)


# Member index page shows all members, and
# ability to send emails to users
@app.route("/send_pass", methods=['GET'])
def send_passes():
    logging.debug("Sending pass page requested")
    membership_passes = db.session.query(Member, Card).join(member_card_association).join(Card).all()
    return render_template('send_passes.html', data=membership_passes)


# Member index page shows all members, and
# ability to send emails to users
@app.route("/create_pass", methods=['GET'])
def create_pass():
    logging.debug("Member page requested")
    data = Member.query.order_by(Member.full_name.desc()).all()
    return render_template('tables.html', members=data)



# Member index page shows all members, and
# ability to send emails to users
@app.route("/upload_data", methods=['GET'])
def upload_membership():
    logging.debug("Member page requested")
    data = Member.query.order_by(Member.full_name.desc()).all()
    return render_template('tables.html', members=data)


# Member index page shows all members, and
# ability to send emails to users
@app.route("/members", methods=['GET'])
def index_members():
    logging.debug("Member index page requested")
    membership = db.session.query(Member).all()
    return render_template('index_members.html', data=membership)


# Member index page shows all members, and
# ability to send emails to users
@app.route("/passes", methods=['GET'])
def index_passes():
    logging.debug("Pass index page requested")
    passes = db.session.query(Card).all()
    return render_template('index_passes.html', data=passes)


# Member index page shows all members, and
# ability to send emails to users
@app.route("/devices", methods=['GET'])
def index_devices():
    logging.debug("Device index page requested")
    devices = db.session.query(Device).all()
    return render_template('index_devices.html', data=devices)



# register user
@app.route('/send_mail', methods=['POST'])
def send_mail():
    print(request.values.get('field', None))
    # return "abc"
    recipient_email = request.values.get('email', None)
    name = request.values.get('name', None)
    logging.debug("send_mail called")
    msg = Message("Digital memberhsip card | Phipps Conservatory and Botanical Gardens",
                  sender="georgeY852@gmail.com",
                  recipients=["georgeY852@gmail.com"])
    msg.html = '''
        Dear {},<br><br>
        Phipps Conservatory is always seeking to continue it's
        mission of reducing it's carbon emissions. One of our new initiatives
        is having our membership cards available by phone. Attached to this
        email is your membership card that can be saved and loaded onto your smartphone device.<br><br>
        For Apple devices:
        <ul>
            <li> If you're on your phone, simply double tap on the attached .pkpass file, and it should automatically
             add to your Apple Wallet.<br>
            <li> If you're on your Macbook, you can also double click on the attached file for it to be added to all
             your Apple devices.
            <br>
            NOTE: This will only work if you've connected your iPhone and Macbook with the same iCloud. If not, you can
             download your .pkpass
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
    filename = "{}.pkpass".format(name.replace(" ", ""))
    with app.open_resource("Pass Files/{}".format(filename)) as fp:
        msg.attach("{}".format(filename), "Pass Files/{}".format(filename), fp.read())
    mail.send(msg)
    logging.debug("mail sent")
    return recipient_email


# Registering a Device to Receive Push Notifications for a Pass
# webServiceURL/version/devices/deviceLibraryIdentifier/registrations/generic/serialNumber
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/<serialNumber>",
           methods=['POST'])
def register_device(version, deviceLibraryIdentifier, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    aPass = Card.query.filter_by(id=serialNumber).first()

    # Verify that version and pass type ID is correct,
    # that serial number on pass exists, and the
    # authentication token is correct
    # If not, return 401 Unauthorized
    if (version != 1) or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership') or (aPass is None) \
            or (aPass.authenticationToken != recievedAuth):
        return not_authorized("Device registration could not be completed.")
    else:
        # Check if device is already registered, and if not
        # then register device
        if len(Device.query().filter_by(device_lib_id=deviceLibraryIdentifier,push_token=request.values.get('pushToken'))) < 1:
            newDevice = Device(device_lib_id=deviceLibraryIdentifier,push_token=request.values.get('pushToken'))
            aPass.devices.append(newDevice)
            db.session.add(aPass)
            db.session.commit()
            return json.dumps({'success': True}), 201, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 200, {'ContentType':'application/json'}


# Getting the Serial Numbers for Passes Associated with a Device
# webServiceURL/<v1>/devices/deviceLibraryIdentifier/registrations/passTypeIdentifier?passesUpdatedSince=tag
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/",methods=['GET'])
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>?passesUpdatedSince=<tag>",
           methods=['GET'])
def get_serial(version, deviceLibraryIdentifier, passTypeIdentifier, tag):
    # Verify that version and pass type ID is correct,
    # that serial number on pass exists, and the
    # authentication token is correct
    # If not, return 401 Unauthorized
    if (version != 1) or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership') \
            or (len(Device.query().filter_by(device_lib_id=deviceLibraryIdentifier)) <1):
        return not_authorized("Device authorization invalid")

    # Look at the registrations table, and determine which passes the device is registered for.
    registrations = Device.query.join(registration).join(Card).\
            filter(registration.c.device_id == deviceLibraryIdentifier).all()

    # Look at the passes table, and determine which passes have changed since the given tag.
    # Don’t include serial numbers of passes that the device didn’t register for.
    # If no update tag is provided, return all the passes that the device is registered for.
    # For example, you return all registered passes the very first time a device communicates with your server.
    if len(registrations > 0):
        # TODO: add Tag check
        serialNumbers = []
        for aRegistration in registrations:
            serialNumbers.append(aRegistration.pass_id)
        return json.dumps({'lastUpdated': datetime.datetime.now(), 'serialNumbers': serialNumbers}),\
               200, {'ContentType': 'application/json'}


# Getting the Latest Version of a Pass
# webServiceURL/version/passes/passTypeIdentifier/serialNumber
# api.sandbox.push.apple.com:443 <- send to this?
@app.route("/<version>/passes/<passTypeIdentifier>/<serialNumber>", methods=['GET'])
def get_latest_version(version, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    if (version != 1) or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership'):
        return not_authorized("Authorization Token does not match")
    else:
        aPass = Card.query.filter_by(id=serialNumber).first()
        if (aPass.authenticationToken == recievedAuth):
            return json.dumps(aPass.data), 200, {'ContentType':'application/vnd.apple.pkpass'}


# Unregistering a Device
# deviceLibraryIdentifier/registrations/passTypeIdentifier/serialNumber
@app.route("/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership/"
           "<serialNumber>", methods=['DELETE'])
def unregister_device(deviceLibraryIdentifier, serialNumber):
    # TODO: unregister device
    return


# Logging errors
# webServiceURL/version/log
@app.route("/v1/log", methods=['POST'])
def logging_error():
    # TODO: log device
    return


# Logic for creating pass
def create_pass():
    # TODO: Should be called from the importing module
    return

# configure queue for training models
queue = Queue(maxsize=100)
thread = threading.Thread(target=create_pass, name='PassSignageDaemon')
thread.setDaemon(False)
thread.start()
