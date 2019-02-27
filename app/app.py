import os
import logging
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from queue import Queue
from flask_mail import Mail
from flask_mail import Message
from flask import send_file, Response
import json
from datetime import datetime
from wallet.models import Pass, Barcode, Generic
import hashlib
import csv

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
    recipient_email = request.values.get('email', None)
    name = request.values.get('name', None)
    authtok = request.values.get('authtok', None)
    logging.debug("send_mail called")
    msg = Message("Digital memberhsip card | Phipps Conservatory and Botanical Gardens",
                  sender="georgeY852@gmail.com",
                  recipients=["gyao@andrew.cmu.edu"])
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
    with app.open_resource("pkpass files/{}".format(filename)) as fp:
        msg.attach("{}".format(filename), "pkpass files/{}".format(filename), fp.read())
    mail.send(msg)
    logging.debug(authtok);
    # TODO: aPass is not being updated
    aPass = Card.query.filter_by(authenticationToken=authtok).first()
    aPass.last_sent = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    db.session.add(aPass)
    db.session.commit()

    logging.debug("mail sent")
    return recipient_email


# Registering a Device to Receive Push Notifications for a Pass
# webServiceURL/version/devices/deviceLibraryIdentifier/registrations/generic/serialNumber
# ex. /v1/devices/fef343fa2fdaaf99f9e3aeb93b13f369/registrations/pass.org.conservatory.phipps.membership/1
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/<serialNumber>",
           methods=['POST'])
def register_device(version, deviceLibraryIdentifier, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    aPass = Card.query.filter_by(id=serialNumber).first()
    # Verify that version and pass type ID is correct,
    # that serial number on pass exists, and the
    # authentication token is correct
    # If not, return 401 Unauthorized
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership') or (aPass is None) \
            or (aPass.authenticationToken != recievedAuth):
        return not_authorized("Device registration could not be completed.")
    else:
        # Check if device is already registered, and if not
        # then register device
        if db.session.query(Device).filter((Device.device_lib_id == deviceLibraryIdentifier)
                                           & (Device.push_token == request.values.get('pushToken'))).first() is None:
            newDevice = Device(date_registered=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                               device_lib_id=deviceLibraryIdentifier,
                               push_token=request.get_json().get('pushToken'))
            aPass.devices.append(newDevice)
            db.session.add(aPass)
            db.session.commit()
            logging.debug("Device registration success!")
            return json.dumps({'success': True}), 201, {'ContentType': 'application/json'}
        else:
            logging.debug("Device already registered!")
            return json.dumps({'success': False}), 200, {'ContentType':'application/json'}


# Getting the Serial Numbers for Passes Associated with a Device
# webServiceURL/<v1>/devices/deviceLibraryIdentifier/registrations/passTypeIdentifier?passesUpdatedSince=tag
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/",methods=['GET'])
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>?passesUpdatedSince=<tag>",
           methods=['GET'])
def get_serial(version, deviceLibraryIdentifier, passTypeIdentifier, tag):
    # TODO: get_serial() missing 1 required positional argument
    # Verify that version and pass type ID is correct,
    # that serial number on pass exists, and the
    # authentication token is correct
    # If not, return 401 Unauthorized
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership') \
            or (db.session.query(Device).filter((Device.device_lib_id == deviceLibraryIdentifier)).first() is None):
        return not_authorized("Device authorization invalid")

    # Look at the registrations table, and determine which passes the device is registered for.
    registrations = Device.query.join(registration).join(Card).\
            filter(registration.c.device_id == deviceLibraryIdentifier).all()

    # Look at the passes table, and determine which passes have changed since the given tag.
    # Don’t include serial numbers of passes that the device didn’t register for.
    # If no update tag is provided, return all the passes that the device is registered for.
    # For example, you return all registered passes the very first time a device communicates with your server.
    if len(registrations) > 0:
        # TODO: add Tag check; related to error above
        serialNumbers = []
        for aRegistration in registrations:
            serialNumbers.append(aRegistration.pass_id)
        logging.debug("Sending list of passes device is registered for")
        return json.dumps({'lastUpdated': datetime.datetime.now(), 'serialNumbers': serialNumbers}),\
               200, {'ContentType': 'application/json'}
    else:
        return not_authorized("No registered devices.")


# Getting the Latest Version of a Pass
# webServiceURL/version/passes/passTypeIdentifier/serialNumber
# api.sandbox.push.apple.com:443 <- send to this?
@app.route("/<version>/passes/<passTypeIdentifier>/<serialNumber>", methods=['GET'])
def get_latest_version(version, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership'):
        return not_authorized("Version and Pass Type invalid")
    else:
        aPass = Card.query.filter_by(id=serialNumber).first()
        if (aPass is not None and aPass.authenticationToken == recievedAuth):
            return send_from_directory('/pkpass files', aPass.file_name,mimetype='application/vnd.apple.pkpass')

# Unregistering a Device
# deviceLibraryIdentifier/registrations/passTypeIdentifier/serialNumber
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/"
           "<serialNumber>", methods=['DELETE'])
def unregister_device(version, deviceLibraryIdentifier, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership'):
        return not_authorized("Version and Pass Type invalid")
    device = db.session.query(Device).filter((Device.device_lib_id == deviceLibraryIdentifier)).get(1)
    # TODO: Properly delete
    cards_device = db.session.query(Card, Device).join(registration).filter(Device.device_lib_id == deviceLibraryIdentifier)

    #for card, device in cards_device:
    for reg in cards_device.registration:
        db.session.delete(reg)
    db.session.commit()
    return


# Logging errors
# webServiceURL/version/log
@app.route("/<version>/log", methods=['POST'])
def logging_error():
    msgs = request.values.get('logs')
    for msg in msgs:
        logging.debug(str(msg))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

# Helper function to find difference
# in the csv files
def find_difference(newcsv):
    try:
        with open('memberdata/last_member.csv', 'r') as t1, open('memberdata/' + newcsv, 'r') as t2:
            fileone = t1.readlines()
            filetwo = t2.readlines()

        with open('memberdata/update.csv', 'w') as outFile:
            for line in filetwo:
                if line not in fileone:
                    outFile.write(line)

        t1.close()
        t2.close()
        outFile.close()
        if os.path.exists('memberdata/last_member.csv'):
            os.remove('memberdata/last_member.csv')
        os.rename('memberdata/' + newcsv, 'memberdata/last_member.csv')
        return True
    except:
        return False

# Helper function to applied for each record
# Read in the updated membership record
# Find respetive card record if exist;
# create or update card record
def create_member_pass(id, member_level, expiration_date, status, full_name,
                associated_members, add_1, add_2, city, state, zip, email):
    # using pass.id as the serial number for now
    try:
        member = Member(id=id, member_level=member_level,
                         expiration_date=datetime.strptime(expiration_date, '%m/%d/%Y'), status=status, full_name=full_name,
                         associated_members=associated_members, address_line_1=add_1, address_line_2=add_2,
                         city=city, state=state, zip=zip, email=email)
        card = Card(authenticationToken=hashlib.sha1(member.id.encode('utf-8')).hexdigest(), file_name=None,
                     last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        cardInfo = Generic()

        # Name, Tier and membership
        cardInfo.addPrimaryField('tier-and-name', member.full_name, member.member_level)
        cardInfo.addSecondaryField('membership-number', member.id, 'Membership Number')

        # Expiration
        if member.expiration_date is not None:
            cardInfo.addSecondaryField('expires', member.expiration_date.strftime("%Y-%m-%d"), 'Expires')
        else:
            cardInfo.addSecondaryField('expires', '', 'Expires')

        # Address, and back fields (including associates)
        fullAddress = member.address_line_1 + ", "
        if member.address_line_2 is not None:
            fullAddress += member.address_line_2 + " "
        fullAddress += member.city + " " + member.state + " " + member.zip
        cardInfo.addAuxiliaryField('address', fullAddress, 'Address Line 1')
        cardInfo.addBackField('associates', member.associated_members, 'Associate Members')
        cardInfo.addBackField('operating-hours', 'Saturday - Thursday: 9:30 a.m. - 5 p.m.\nFriday: 9:30 a.m. - 10 p.m.',
                              'Hours')
        cardInfo.addBackField('member-info', '(412)-315-0656\nmembers@phipps.conservatory.org', 'Member Info')
        cardInfo.addBackField('address',
                              'One Schenley Park | Pittsburgh, Pa. 15213\n412/622-6914 | phipps.conservatory.org',
                              'Address')
        # Card properties
        organizationName = 'Phipps Conservatory & Botanical Garden'
        passTypeIdentifier = 'pass.org.conservatory.phipps.membership'
        teamIdentifier = 'M6LYJ8LVCL'
        passfile = Pass(cardInfo, passTypeIdentifier=passTypeIdentifier, organizationName=organizationName,
                        teamIdentifier=teamIdentifier)
        passfile.logoText = 'Phipps Conservatory'
        passfile.description = 'Phipps Conservatory membership pass for {}'.format(member.full_name)
        passfile.serialNumber = str(card.id)
        passfile.barcode = Barcode(message=str(member.id))
        # TODO: Add locations
        # passfile.locations = Pass.Lff
        passfile.foregroundColor = 'rgb(255, 255, 255)'
        passfile.backgroundColor = 'rgb(121, 161, 56)'
        passfile.labelColor = 'rgb(255, 255, 255)'

        # Icon and Logo needed for pass to be successfully created
        passfile.addFile('icon.png', open('pass utility folder/PhippsSampleGeneric.pass/logo.png', 'rb'))
        passfile.addFile('logo.png', open('pass utility folder/PhippsSampleGeneric.pass/logo.png', 'rb'))
        passfile.webServiceURL = 'https://phippsconservatory.xyz'
        passfile.authenticationToken = str(card.authenticationToken)
        passfile.create('certificates/certificate.pem', 'certificates/key.pem', 'certificates/wwdr.pem',
                        os.environ['PEM_PASSWORD'],
                        './pkpass files/{}.pkpass'.format(member.full_name.replace(" ", "")))
        member.cards.append(card)
        db.session.add(member)
        db.session.commit()
        return True
    except:
        logging.debug("Exception occured when trying to member, and card.")
        return False



# configure queue for training models
# queue = Queue(maxsize=100)
# thread = threading.Thread(target=create_pass, name='PassSignageDaemon')
# thread.setDaemon(False)
# thread.start()
