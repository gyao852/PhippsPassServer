from app import db
from sqlalchemy.dialects.postgresql import JSON

class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.String(100), primary_key=True)
    member_level = db.Column(db.String(100))
    full_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    expiration_date = db.Column(db.DateTime)
    associated_members = db.Column(db.String(100)) # May need to remove
    address_line_1 = db.Column(db.String(100), nullable=False)
    address_line_2 = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    passes = db.relationship('Pass', backref='member', lazy=True)

    def __init__(self, id, member_level, full_name, status, expiration_date,associated_members,
                    address_line_1,address_line_2,city,state,zip,email,passes=[]):
        self.id = id
        self.member_level = member_level
        self.full_name = full_name
        self.status = status
        self.expiration_date = expiration_date
        self.associated_members = associated_members
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.state = state
        self.zip = zip
        self.email = email
        self.passes = passes
        # newPass = Pass("pass.org.conservatory.phipps.membership",00001)
        # db.session.add(member1)

    # def __repr__(self):
    #     # return {self.full_name,0}
    #     return '{}'.format(self.full_name)

class Pass(db.Model):
    __tablename__ = 'pass'
    pass_type_id = db.Column(db.String(100), primary_key=True)
    serial_number = db.Column(db.String(100), primary_key=True)
    file_name = db.Column(db.String(100))
    member_id = db.Column(db.String(100), db.ForeignKey('member.id'), nullable=False)
    active = db.Column(db.Boolean)
    last_sent = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __init__(self, pass_type_id, serial_number, file_name, active,
                member_id, last_sent, last_updated):
        self.pass_type_id = pass_type_id
        self.serial_number = serial_number
        self.file_name = file_name
        self.active = active
        self.member_id = member_id
        self.last_sent = last_sent
        self.last_updated = last_updated

    # def __repr__(self):
    #     return 'id {}'.format(self.id)

class Device(db.Model):
    __tablename__ = 'device'
    device_lib_id = db.Column(db.String(100), primary_key=True)
    push_token = db.Column(db.String(100))

    def __init__(self, device_lib_id, push_token):
        self.device_lib_id = device_lib_id
        self.push_token = push_token

    # def __repr__(self):
    #     return 'id {}'.format(self.id)

# 
# registrations = db.Table('registrations',
#     db.Column('device_device_lib_id', db.String(100), db.ForeignKey('device.device_lib_id'), primary_key=True),
#     db.Column('pass_serial_number', db.String(100), db.ForeignKey('pass.serial_number'), primary_key=True),
#     db.Column('pass_pass_type_id', db.String(100), db.ForeignKey('pass.pass_type_id'), primary_key=True))
