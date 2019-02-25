import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from models import Member, Pass, Device
from datetime import datetime
import secrets
import json
import subprocess

app.config.from_object(os.environ['APP_SETTINGS'])
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def seed():
    "Adding seed data to the database"
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


    pass1AuthToken = secrets.token_hex(12)
    pass2AuthToken = secrets.token_hex(12)
    pass3AuthToken = secrets.token_hex(12)
    pass4AuthToken = secrets.token_hex(12)
    pass1 = Pass(authenticationToken=pass1AuthToken,file_name=None,
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass2 = Pass(authenticationToken=pass2AuthToken,file_name=None,
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass3 = Pass(authenticationToken=pass3AuthToken,file_name=None,
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    pass4 = Pass(authenticationToken=pass4AuthToken,file_name=None,
                 last_sent=None, last_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    allMembers = {member1: pass1, member2: pass2, member3: pass3, member4: pass4}



    # using pass.id as the serial number for now
    # Python dictionary represntation of json pass file:
    for member, aPass in allMembers.items():
        with open('passTemplate.json') as f:
            data = json.load(f)
            data['serialNumber'] = str(aPass.id)
            data['webServiceURL'] = 'phipps-conservatory-passes.us-east-1.elasticbeanstalk.com'
            data['authenticationToken'] = aPass.authenticationToken
            data['barcode']['message'] = member.id
            data['generic']['primaryFields'][0]['label'] = member.full_name
            data['generic']['primaryFields'][0]['value'] = member.member_level
            data['generic']['secondaryFields'][0]['value'] = member.id
            if member.expiration_date is not None:
                print(member.expiration_date)
                print(member.expiration_date.strftime("%Y-%m-%dT%H:%M:%S"))
                data['generic']['secondaryFields'][1]['value'] = member.expiration_date.strftime("%Y-%m-%dT19:30-06:00")
            else:
                data['generic']['secondaryFields'][1]['value'] = ''
            fullAddress = member.address_line_1
            if member.address_line_2 is not None:
                fullAddress += ", " + member.address_line_2 + " "
            fullAddress += member.city + " " + member.state + " " + member.zip
            data['generic']['auxiliaryFields'][0]['value'] = fullAddress
            data['generic']['backFields'][0]['value'] = member.associated_members
            f.seek(0) # reset cursor to beginning
            with open('PhippsSampleGeneric.pass/pass.json', 'w') as outfile:
                json.dump(data, outfile)
            print()
            os.system("./signpass -p PhippsSampleGeneric.pass -o Pass\ Files/{}.pkpass".format(member.full_name.replace(" ","")))
            aPass.file_name = '{}.pkpass'.format(member.full_name.replace(" ","")) # TODO: replace this with relative path
    member1.passes.append(pass1)
    member2.passes.append(pass2)
    member3.passes.append(pass3)
    member4.passes.append(pass4)
    db.session.add(member1)
    db.session.add(member2)
    db.session.add(member3)
    db.session.add(member4)
    db.session.add(member5)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
