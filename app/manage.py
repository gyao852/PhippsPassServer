import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import time
from datetime import datetime
from app import app, db
from models import Member, Pass
app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def seed():
    "Adding seed data to the database"
    Member.query.delete()
    member1 = Member('8-11111111', 'Student', 'George Yao', True, datetime.strptime('05/14/2019', '%m/%d/%Y'), 'Jason Yao',
                     '1063 Morewood Avenue', None, 'Pittsburgh', 'PA', '15213', 'gyao@andrew.cmu.edu', [])
    member2 = Member('8-10060865', 'Employee', 'Mike Cassidy', True, datetime.strptime('12/31/2019', '%m/%d/%Y'), 'Michael Cassidy, Jason Gamrath and Dale Chihuly',
                     '6327 Waldron Street', None, 'Pittsburgh', 'PA', '15217', 'mcassidy@phipps.conservatory.org', [])
    member3 = Member('8-10060972', 'Employee', 'Dara Goldhagen', True, datetime.strptime('1/31/2020', '%m/%d/%Y'), 'Dara Goldhagen',
                     '6341 Glenview Place', None, 'Pittsburgh', 'PA', '15206', 'dgoldhagen@gmail.com', [])
    member4 = Member('8-10061037', 'Employee', 'Monica Marchese', True, datetime.strptime('12/31/2022', '%m/%d/%Y'), 'Ms. Monica Marchese',
                     '90 South 25th Street', 'Apartment 2', 'Pittsburgh', 'PA', '15203', 'mmarchese@phipps.conservatory.org', [])
    member5 = Member('8-10061046', 'Employee', 'Nalitz Christine', True, None, None,
                     'Phipps Conservatory and Botanical Gardens', 'One Schenley Park', 'Pittsburgh', 'PA', '15213', 'cnalitz@phipps.conservatory.org', [])
    db.session.add(member1)
    db.session.add(member2)
    db.session.add(member3)
    db.session.add(member4)
    db.session.add(member5)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
