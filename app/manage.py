import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from models import Member, Card, Device
from datetime import datetime
from wallet.models import Pass, Barcode, Generic
import hashlib

app.config.from_object(os.environ['APP_SETTINGS'])
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def seed():
    "Adding seed data to the database"
    print("Adding data")
    db.session.commit()
    db.drop_all()
    db.create_all()

    member1 = Member(id='8-11111111', member_level='Student',
                     expiration_date=datetime.strptime('12/31/2019', '%m/%d/%Y'), status=True, full_name='George Yao',
                     associated_members='Jason Yao', address_line_1='1063 Morewood Avenue', address_line_2=None,
                     city='Pittsburgh', state='PA', zip='15213', email='gyao@andrew.cmu.edu')
    member2 = Member(id='8-10060865', member_level='Employee',
                     expiration_date=datetime.strptime('12/31/2019', '%m/%d/%Y'), status=True, full_name='Mike Cassidy',
                     associated_members='Michael Cassidy, Jason Gamrath and Dale Chihuly',
                     address_line_1='6327 Waldron Street', address_line_2=None,
                     city='Pittsburgh', state='PA', zip='15217', email='mcassidy@phipps.conservatory.org')
    member3 = Member(id='8-10060972', member_level='Employee',
                     expiration_date=datetime.strptime('1/31/2020', '%m/%d/%Y'),
                     status=True, full_name='Dara Goldhagen', associated_members='Dara Goldhagen',
                     address_line_1='6341 Glenview Place', address_line_2=None, city='Pittsburgh', state='PA',
                     zip='15206', email='dgoldhagen@gmail.com')
    member4 = Member(id='8-10061037', member_level='Employee',
                     expiration_date=datetime.strptime('12/31/2022', '%m/%d/%Y'), status=True,
                     full_name='Monica Marchese', associated_members='Ms. Monica Marchese',
                     address_line_1='90 South 25th Street', address_line_2='Apartment 2', city='Pittsburgh', state='PA',
                     zip='15203', email='mmarchese@phipps.conservatory.org')
    member5 = Member(id='8-10061046', member_level='Employee',
                     expiration_date=None, status=True,  full_name='Nalitz Christine',
                     associated_members=None, address_line_1='Phipps Conservatory and Botanical Gardens',
                     address_line_2='One Schenley Park',
                     city='Pittsburgh', state='PA', zip='15213', email='cnalitz@phipps.conservatory.org')
    member6 = Member(id='8-11111112', member_level='Senior Citizen',
                     expiration_date=datetime.strptime('12/31/2019', '%m/%d/%Y'), status=True,  full_name='Larry Heimann',
                     associated_members=None, address_line_1='5000 Forbes Ave',
                     address_line_2=None,
                     city='Pittsburgh', state='PA', zip='15213', email='profh@cmu.edu')

    pass1 = Card(authenticationToken=hashlib.sha1(member1.id.encode('utf-8')).hexdigest(), file_name="GeorgeYao.pkpass",
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass2 = Card(authenticationToken=hashlib.sha1(member2.id.encode('utf-8')).hexdigest(), file_name="MikeCassidy.pkpass",
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass3 = Card(authenticationToken=hashlib.sha1(member3.id.encode('utf-8')).hexdigest(), file_name="DaraGoldhagen.pkpass",
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass4 = Card(authenticationToken=hashlib.sha1(member4.id.encode('utf-8')).hexdigest(), file_name="MonicaMarchese.pkpass",
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass6 = Card(authenticationToken=hashlib.sha1(member6.id.encode('utf-8')).hexdigest(), file_name="LarryHeimann.pkpass",
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    member1.cards.append(pass1)
    member2.cards.append(pass2)
    member3.cards.append(pass3)
    member4.cards.append(pass4)
    member6.cards.append(pass6)
    db.session.add(member1)
    db.session.add(member2)
    db.session.add(member3)
    db.session.add(member4)
    db.session.add(member5)
    db.session.add(member6)

    db.session.commit()
    allMembers = {member1: pass1, member2: pass2, member3: pass3, member4: pass4}

    # using pass.id as the serial number for now
    for member, aPass in allMembers.items():
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
        fullAddress = member.address_line_1  + ", "
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
        passfile.serialNumber = str(aPass.id)
        passfile.barcode = Barcode(message=str(member.id))
        # TODO: Add locations
        # passfile.locations = Pass.Lff
        passfile.foregroundColor='rgb(255, 255, 255)'
        passfile.backgroundColor='rgb(121, 161, 56)'
        passfile.labelColor='rgb(255, 255, 255)'

        # Icon and Logo needed for pass to be successfully created
        passfile.addFile('icon.png', open('pass utility folder/PhippsSampleGeneric.pass/logo.png', 'rb'))
        passfile.addFile('logo.png', open('pass utility folder/PhippsSampleGeneric.pass/logo.png', 'rb'))
        passfile.webServiceURL = 'https://phippsconservatory.xyz'
        passfile.authenticationToken = str(aPass.authenticationToken)
        passfile.create('certificates/certificate.pem', 'certificates/key.pem', 'certificates/wwdr.pem',
                        os.environ['PEM_PASSWORD'],
                        './pkpass files/{}.pkpass'.format(member.full_name.replace(" ", "")))

    member1.cards.append(pass1)
    member2.cards.append(pass2)
    member3.cards.append(pass3)
    member4.cards.append(pass4)
    member6.cards.append(pass6)
    db.session.add(member1)
    db.session.add(member2)
    db.session.add(member3)
    db.session.add(member4)
    db.session.add(member5)
    db.session.add(member6)
    db.session.commit()
    print("Successfully added seed data")


if __name__ == '__main__':
    manager.run()