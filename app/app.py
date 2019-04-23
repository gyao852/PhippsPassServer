from flask import Flask, request, jsonify, render_template, send_from_directory, flash, redirect
from werkzeug.utils import secure_filename
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_mail import Message
from wallet.models import Pass, Barcode, Generic
import hashlib
from pushjack import APNSClient
import os
import logging
import json
from datetime import datetime
import shutil
import pandas as pd
from pytz import timezone
import csv

# import threading


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

# Other Application Configuerations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['SERVER_EMAIL']
app.config['MAIL_PASSWORD'] = os.environ['SERVER_EMAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['PASS_FOLDER'] = './pkpass_files'
app.config['CERTIFICATES_FOLDER'] = './certificates'
app.config['UPLOAD_FOLDER'] = './uploaded_membership_data'
mail = Mail(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
ALLOWED_EXTENSIONS = set(['csv'])

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] - %(threadName)-10s : %(message)s')

from models import Member, Card, Device, member_card_association, registration

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)


# ERROR HANDLERS
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


# MAIN ROUTES

# Main Dashboard
# GET phippsconservatory.xyz/, phippsconservatory.xyz/index.html
@app.route("/", methods=['GET'])
@app.route("/index.html", methods=['GET'])
def index():
    members = Member.query.all()
    passes = Card.query.all()
    devices = Device.query.all()
    registeredPasses = db.engine.execute("select card_id from card_device_association GROUP BY card_id;")
    registeredPassesCount = 0
    for row in registeredPasses:
        registeredPassesCount+=1

    sentRequests = len(Card.query.filter(Card.last_sent != None).all())

    return render_template('index.html', memberCnt=len(members), passCnt=len(passes), deviceCnt=len(devices),
                           pendingCnt=sentRequests-registeredPassesCount)


# Upload membership.csv file
# GET phippsconservatory.xyz/upload_membership
@app.route("/upload_membership", methods=['GET', 'POST'])
def upload_membership():
    if request.method == 'POST':
        logging.debug("In POST upload_membership")
        # check if the post request has the file part
        if 'file' not in request.files:
            logging.debug("There is no file attached")
            return jsonify({'count': 0})
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            logging.debug("There is no file attached")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # last_member.csv is the last uploaded
            # filename is current file being uploaded name
            # find_differnce creates a update.csv, the difference
            # between the two files.
            count = 0
            if find_difference(filename):
                logging.debug("ENTERING INSERTUPDATE()")
                count = insertUpdate()
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "update.csv"))
            else:
                logging.debug("Difference wasn't properly calculated!")
                return jsonify({'count': 0})
        return jsonify({'count': count})
    return render_template('upload_membership.html')


# Send Pass page
# GET phippsconservatory.xyz/send_pass
@app.route("/send_pass", methods=['GET'])
def send_passes():
   # data = db.session.query(Member, Card, Device).join(member_card_association).join(Card).outerjoin(registration).outerjoin(Device).all();
    #  .join(member_card_association).outerjoin(Card).outerjoin(
        #registration).outerjoin(Device).all()
    data = db.engine.execute("select member.id as member_id, member.full_name AS member_full_name, " +
                             "member.member_level AS member_member_level, " +
                             "member.expiration_date AS member_expiration_date, " +
                             "card.last_updated AS card_last_updated, registered.date_registered as registered_date_registered, card.last_sent as card_last_sent, " +
                             "member.email as member_email, 'authenticationToken' AS card_authentication_Token FROM Member " +
                             "INNER JOIN member_card_association ON member_card_association.member_id=member.id " +
                             "INNER JOIN card ON member_card_association.card_id = card.id " +
                             "LEFT JOIN (select date_registered, card_id FROM device "+
                             "JOIN card_device_association ON card_device_association.device_id = device.id " +
                             "WHERE id IN (select device_id FROM (select card_id, device_id, " +
                             "ROW_NUMBER() OVER (PARTITION BY card_ID) as rn from card_device_association " +
                             "GROUP BY card_id, device_id) t where t.rn=1)) AS registered ON registered.card_id = card.id;")
    return render_template('send_passes.html', data=data)


# Send mail containing pass to member
# POST phippsconservatory.xyz/send_mail
@app.route('/send_mail', methods=['POST'])
def send_mail():
    member_name = request.values.get('name', None)
    if member_name is not None:
        member_auth = request.values.get('authtok', None)
        member_email = request.values.get('email', None)
        selectedMembers = [{"name": member_name, "email": member_email, "auth": member_auth}]
    else:
        selectedMemberData = request.form.listvalues()
        selectedMembers = eval(next(selectedMemberData)[0])
    count = 0
    for member in selectedMembers:
        count += 1
        member_email = member["email"]
        member_name = member["name"]
        member_auth = member["auth"]
        msg = Message("Digital Membership Card | Phipps Conservatory and Botanical Gardens",
                      sender="georgeY852@gmail.com",
                      recipients=[member_email])
        msg.html = '''
            Dear {},<br><br>
            Phipps Conservatory is continuing its mission of reducing our carbon footprint. 
            One of our new initiatives is providing members with their membership cards available digitally 
            within your phone. Attached to this email is your membership card that can be saved and loaded
             onto your devices.
            <br><br>
            If you are using an iPhone: 
            <ul>
                <li> Double tap on the attached .pkpass file. 
                You will be prompted to add your new membership pass to the 'Wallet' Application <br>
                <li> On the top right, tap on 'Add'
                <br>
                NOTE: This will only work if you've connected your iPhone and MacBook with the same iCloud. If not, you can
                 download your .pkpass file, and 'Airdrop' it to your iPhone.
            </ul>
            If you are using an Android phone:<br>
            <ul>
                <li> Go to the Google Play Store, and install the application 'Passes''<br>
                <li> Once 'Passes' is installed, double tap on the attached .pkpass file. You will be asked which 
                application to choose from to open this file. Tap on 'Passes<br>
            </ul>
            <br>
            
            This digital membership pass is available for use even when your device is not connected to the Internet, 
            and thus can be used anytime after saving it to your phone. Updates to your membership will be reflected on 
            the next business day, and will require access to the Internet. <br>
            If you have any further questions regarding your digital pass, please feel free to contact us. 
            We hope to see you visit again soon!<br><br>
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
            '''.format(member_name.split(" ")[0])

        filename = "{}.pkpass".format(member_name.replace(" ", ""))
        with app.open_resource("pkpass_files/{}".format(filename)) as fp:
            msg.attach("{}".format(filename), "pkpass_files/{}".format(filename), fp.read())
        mail.send(msg)
        aPass = Card.query.filter_by(authenticationToken=member_auth).first()

        if aPass is not None:
            aPass.last_sent = datetime.now().astimezone(timezone('EST5EDT')).strftime("%Y-%m-%dT%H:%M:%S")
            db.session.add(aPass)
            db.session.commit()
        else:
            return jsonify({'count': 0})
    return jsonify({'count': count})


# GET phippsconservatory.xyz/reset_database
@app.route("/reset_database", methods=['POST'])
def reset_db():
    meta = db.metadata
    try:
        for table in reversed(meta.sorted_tables):
            logging.debug('Clear table %s' % table)
            db.session.execute(table.delete())
        db.session.commit()

        # Clear upload folder
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], "update.csv")):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "update.csv"))
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv")):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"))

        # Clear previously generated passes
        for filename in os.listdir(app.config['PASS_FOLDER']):
            try:
                if os.path.isfile(os.path.join(app.config['PASS_FOLDER'], filename)):
                    os.remove(os.path.join(app.config['PASS_FOLDER'], filename))
            except:
                pass
        return jsonify({"Status": "success"})
    except:
        return jsonify({"Status": "fail"})


# Registering Device to Receive Push Notifications for future updates for a pass
# POST phippsconservatory.xyz/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership/<serialNumber>
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
            newDevice = Device(
                date_registered=datetime.now().astimezone(timezone('EST5EDT')).strftime("%Y-%m-%dT%H:%M:%S"),
                device_lib_id=deviceLibraryIdentifier,
                push_token=request.get_json().get('pushToken'))
            aPass.devices.append(newDevice)
            db.session.add(aPass)
            db.session.commit()
            return json.dumps({'success': True}), 201, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Retrieve all serial numbers (passes) for device
# GET phippsconservatory.xyz/devices/<deviceLibraryIdentifier/registrations/pass.org.conservatory.phipps.membership?passesUpdatedSince=tag
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/", methods=['GET'])
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>?passesUpdatedSince=<tag>",
           methods=['GET'])
def get_serial(version, deviceLibraryIdentifier, passTypeIdentifier):
    # Verify that version and pass type ID is correct,
    # that serial number on pass exists, and the
    # authentication token is correct
    # If not, return 401 Unauthorized
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership') \
            or (db.session.query(Device).filter((Device.device_lib_id == deviceLibraryIdentifier)).first() is None):
        return not_authorized("Device authorization invalid")
    tag = request.args.get("tag");

    # Look at the registrations table, and determine which passes the device is registered for.
    # Note: Tag is an optional query parameter
    if tag is not None:
        registrations = Device.query.join(registration).join(Card). \
            filter(registration.c.device_id == deviceLibraryIdentifier).filter(Card.last_updated >= tag).all()
    else:
        registrations = Device.query.join(registration).join(Card). \
            filter(registration.c.device_id == deviceLibraryIdentifier).all()

    # Look at the passes table, and determine which passes have changed since the given tag.
    # Don’t include serial numbers of passes that the device didn’t register for.
    # If no update tag is provided, return all the passes that the device is registered for.
    # For example, you return all registered passes the very first time a device communicates with your server.
    if len(registrations) > 0:
        serialNumbers = []
        for aRegistration in registrations:
            serialNumbers.append(aRegistration.pass_id)
        logging.debug("Sending list of passes device is registered for")
        return json.dumps(
            {'lastUpdated': datetime.datetime.now().astimezone(timezone('EST5EDT')), 'serialNumbers': serialNumbers}), \
               200, {'ContentType': 'application/json'}
    else:
        logging.debug("No registrations found! Should at least be one.")
        return not_authorized("No registered devices.")


# Get latest version of a Pass
# GET phippsconservatory.xyz/v1/passes/pass.org.conservatory.phipps.membership/<serialNumber>
@app.route("/<version>/passes/<passTypeIdentifier>/<serialNumber>", methods=['GET'])
def get_latest_version(version, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership'):
        return not_authorized("Version and Pass Type invalid")
    else:
        aPass = Card.query.filter_by(id=serialNumber).first()
        if (aPass is not None and aPass.authenticationToken == recievedAuth):
            return send_from_directory(app.config['PASS_FOLDER'], aPass.file_name,
                                       mimetype='application/vnd.apple.pkpass')


# Unregistering a Device
# DELETE phippsconservatory.xyz/v1/devices/<deviceLibraryIdentifier>/registrations/pass.org.conservatory.phipps.membership/<serialNumber>
@app.route("/<version>/devices/<deviceLibraryIdentifier>/registrations/<passTypeIdentifier>/"
           "<serialNumber>", methods=['DELETE'])
def unregister_device(version, deviceLibraryIdentifier, passTypeIdentifier, serialNumber):
    recievedAuth = request.headers.get('Authorization').split(" ")[1]
    if (version != 'v1') or (passTypeIdentifier != 'pass.org.conservatory.phipps.membership'):
        return not_authorized("Version and Pass Type invalid")
    device = db.session.query(Device).filter((Device.device_lib_id == deviceLibraryIdentifier)).first()
    # TODO: Conduct stress tests to test this more
    try:
        cards_device = db.session.query(Card, Device).join(registration).filter(
            Device.device_lib_id == deviceLibraryIdentifier).first()[1]
        # for card, device in cards_device:
        for reg in cards_device:
            db.session.delete(reg)
        db.session.commit()
    except:
        return
    return


# Logs errors
# POST phippsconservatory.xyz/v1/log
@app.route("/<version>/log", methods=['POST'])
def logging_error(version):
    msgs = request.json
    if (version != 'v1'):
        return not_authorized("version is invalid")
    for msg in msgs['logs']:
        logging.debug(str(msg))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# Following is for development ONLY, remove routes and update sidebar for final deployment

# Show all members
# GET phippsconservatory.xyz/members
@app.route("/members", methods=['GET'])
def index_members():
    membership = db.session.query(Member).all()
    return render_template('index_members.html', data=membership)


# Show all passes
# GET phippsconservatory.xyz/members
@app.route("/passes", methods=['GET'])
def index_passes():
    passes = db.session.query(Card).all()
    return render_template('index_passes.html', data=passes)


# Show all devices
# ability to send emails to users
@app.route("/devices", methods=['GET'])
def index_devices():
    devices = db.session.query(Device).all()
    return render_template('index_devices.html', data=devices)


# PRIVATE HELPER FUNCTIONS

# Reading from a provided update.csv file, it will traverse
# record by record of the file, inserting new records or
# updating existing ones
def insertUpdate():
    logging.debug("In insertUpdate()")
    update_file = os.path.join(app.config['UPLOAD_FOLDER'], "update.csv")
    try:
        df = pd.read_csv(update_file)
    except:
        return -1
    df.columns = ["id", "level", "expiration_date", "status", "associates", "last_name", "first_name",
                  "address_1", "address_2", "city", "state", "zip", "email", "add_ons", "quantity"]
    diff_count = 0
    try:
        for row in df.itertuples():
            logging.debug("Checking a row")
            logging.debug(row.id)
            if str(row.id) == None or row.id == '' or pd.isnull(row.id):
                break

            diff_count += 1
            existing_mem = Member.query.filter_by(id=row.id).first()
            state = False
            exp_date = None
            add_2 = row.address_2
            if row.status == 'Active':
                state = True
            else:
                state = False
            if pd.isna(row.expiration_date) is False:
                for fmt in ('%m/%d/%Y', '%m/%d/%y'):
                    try:
                        exp_date = datetime.strptime(row.expiration_date, fmt).astimezone(timezone('EST5EDT'))
                    except ValueError:
                        pass
            if pd.isna(row.address_2):
                add_2 = None
            if existing_mem is None:
                existing_mem = Member(id=str(row.id), member_level=str(row.level),
                                      expiration_date=exp_date, status=state,
                                      full_name=row.first_name + " " + row.last_name,
                                      associated_members=row.associates, address_line_1=str(row.address_1),
                                      address_line_2=add_2,
                                      city=str(row.city), state=str(row.state), zip=str(row.zip).strip(".0"),
                                      email=str(row.email),
                                      add_on_name=row.add_ons,
                                      add_on_value=str(row.quantity).strip(".0"))
                db.session.add(existing_mem)
                db.session.commit()
            else:
                logging.debug("Updating existing member information")
                # Update existing member record
                existing_mem.member_level = row.level
                existing_mem.expiration_date = exp_date
                existing_mem.status = state
                existing_mem.full_name = row.first_name + " " + row.last_name
                existing_mem.associated_members = row.associates
                existing_mem.address_1 = row.address_1
                existing_mem.address_2 = add_2
                existing_mem.city = row.city
                existing_mem.state = row.state
                existing_mem.zip = row.zip
                existing_mem.email = row.email
                logging.debug("Completed")

            # Create a new pass (for both new and updates)
            if exp_date is not None:
                logging.debug("Creating/updating pass because expiration date is not None")
                # A previous card record exists
                try:
                    logging.debug("Previous card was found")
                    card = db.session.query(Member, Card).join(member_card_association).join(Card).filter(
                        member_card_association.c.member_id == row.id).first()[1]
                    card.last_updated = datetime.now().astimezone(timezone('EST5EDT')).strftime(
                        "%Y-%m-%dT%H:%M:%S")
                except:
                    # Make a new card
                    logging.debug("New card created")
                    card = Card(authenticationToken=hashlib.sha1(existing_mem.id.encode('utf-8')).hexdigest(),
                                file_name=row.first_name + row.last_name + ".pkpass",
                                last_sent=None,
                                last_updated=datetime.now().astimezone(timezone('EST5EDT')).strftime(
                                    "%Y-%m-%dT%H:%M:%S"))
                # Attach it to membership
                existing_mem.cards.append(card)
                db.session.add(existing_mem)
                db.session.commit()
                logging.debug("Card has been added to associated member record")

                # Create the actual pass file
                logging.debug("Creating actual card now")
                create_member_pass(row.id, card.file_name)

                # Notify devices attached to this card
                registrations = Device.query.join(registration).join(Card). \
                    filter(registration.c.card_id == card.id).all()
                for device in registrations:
                    logging.debug("Attempting to send push to APN")
                    token = device.push_token
                    alert = {};
                    client = APNSClient(
                        certificate=os.path.join(app.config['CERTIFICATES_FOLDER'], "apn_certificate.pem"),
                        default_error_timeout=10,
                        default_expiration_offset=2592000,
                        default_batch_size=100,
                        default_retries=5)
                    res = client.send(token, alert)
                    logging.debug(res.errors)
                    logging.debug(res.failures)
                    logging.debug(res.message)
                    logging.debug(res.successes)
                    # TODO: if APNs tells you that a push token is invalid,
                    #  remove that device and its registrations from your server.
                    client.close()
                    db.session.commit()
    except IOError:
        return diff_count
    return diff_count


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Finds differences between two membership csv files,
# deletes the old csv membership file with the new one
# and creates a update.csv file with the difference
def find_difference(newcsv):
    # If no previous membership data is in postGres
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv")) is False:
        os.rename(os.path.join(app.config['UPLOAD_FOLDER'], newcsv),
                  os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"))
        shutil.copyfile(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"),
                        os.path.join(app.config['UPLOAD_FOLDER'], "update.csv"))
        return True
    try:
        columns = ["id", "level", "expiration_date", "status", "associates", "last_name", "first_name",
                   "address_1", "address_2", "city", "state", "zip", "email", "add_ons", "quantity"]
        logging.debug("1. Attempting to find difference of uploaded file")

        # encoding='utf-8' and then try with errors='replace'
        # rb is read via bytes; trying manual encoding for now
        # No longer a read permission error but a stupid pesky decode error
        with open(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"), 'r', encoding='utf-8') as t1, open(
                os.path.join(app.config['UPLOAD_FOLDER'], newcsv), 'r', encoding='utf-8') as t2:
            try:
                fileone = t1.readlines()
                filetwo = t2.readlines()
                logging.debug("2. Passed readlines()")
            except Exception as e:
                logging.debug(type(e).__name__)
                logging.debug(e)

        logging.debug("3. Now comparing line by line")
        # Use sets in the future for faster processing
        with open(os.path.join(app.config['UPLOAD_FOLDER'], "update.csv"), 'w', encoding='utf-8') as outFile:
            writer = csv.writer(outFile)
            # writer.writerow(columns)
            for line in filetwo:
                if line not in fileone:
                    outFile.write(line)

        t1.close()
        t2.close()
        outFile.close()
        logging.debug("7. Attempting to find difference of uploaded file")
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv")):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"))
        os.rename(os.path.join(app.config['UPLOAD_FOLDER'], newcsv),
                  os.path.join(app.config['UPLOAD_FOLDER'], "last_member.csv"))
        return True
    except:
        logging.debug("Some reading error has occured")
        return False


# Creates or update a card record for a single member record
def create_member_pass(id, filename):
    if os.path.isfile(os.path.join(app.config['PASS_FOLDER'], filename)):
        os.remove(os.path.join(app.config['PASS_FOLDER'], filename))

    logging.debug("Looking for Member and card records")
    member = Member.query.filter_by(id=id).first()
    card = db.session.query(Member, Card).join(member_card_association).join(Card).filter(
        member_card_association.c.member_id == member.id).first()[1]
    logging.debug("Member and card record have been found")
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
    fullAddress += member.city + " " + member.state + " " + str(member.zip)
    cardInfo.addAuxiliaryField('address', fullAddress, 'Address Line 1')
    cardInfo.addBackField('associates', member.associated_members, 'Associate Members')
    # if member.additional_child is not None:
    # cardInfo.addBackField('addons', member.additiona_child, 'Add-ons')
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
    # Value for key 'locations' must be of class NSArray, but is actually of class __NSDictionaryI."
    # Tried to fix manually but too convoluted
    # passfile.locations = Location(latitude=40.4392, longitude=-79.9474)
    passfile.foregroundColor = 'rgb(255, 255, 255)'
    passfile.backgroundColor = 'rgb(121, 161, 56)'
    passfile.labelColor = 'rgb(255, 255, 255)'

    # Icon and Logo needed for pass to be successfully created
    passfile.addFile('icon.png', open('pass_utility/PhippsSampleGeneric.pass/logo.png', 'rb'))
    passfile.addFile('logo.png', open('pass_utility/PhippsSampleGeneric.pass/logo.png', 'rb'))
    passfile.webServiceURL = 'https://phippsconservatory.xyz'
    passfile.authenticationToken = str(card.authenticationToken)
    passfile.create(os.path.join(app.config['CERTIFICATES_FOLDER'], "certificate.pem"),
                    os.path.join(app.config['CERTIFICATES_FOLDER'], "key.pem"),
                    os.path.join(app.config['CERTIFICATES_FOLDER'], "wwdr.pem"),
                    os.environ['PEM_PASSWORD'],
                    os.path.join(app.config['PASS_FOLDER'], member.full_name.replace(" ", "") + ".pkpass"))
    logging.debug("Card created!!!")
    return True

# Configure multithreading in the future for async processing of member data
# thread = threading.Thread(target=upload_membership, name='TrainingDaemon')
# thread.setDaemon(False)
# thread.start()
