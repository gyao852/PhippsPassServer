from app import db


member_pass_association = db.Table('member_pass_association', db.Model.metadata,
                                   db.Column('member_id', db.String(100), db.ForeignKey('member.id')),
                                   db.Column('pass_id', db.Integer, db.ForeignKey('pass.id')))


class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.String(100), primary_key=True, nullable=False)
    member_level = db.Column(db.String(100))
    expiration_date = db.Column(db.DateTime)
    status = db.Column(db.Boolean)
    full_name = db.Column(db.String(100), nullable=False)
    associated_members = db.Column(db.String(100))  # May need to remove
    address_line_1 = db.Column(db.String(100))
    address_line_2 = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False)
    passes = db.relationship('Pass', secondary=member_pass_association)

# don't know why, but association table created when added primary_key=True? even though no need for above
registration = db.Table('pass_device_association', db.Model.metadata,
                                   db.Column('pass_id', db.Integer, db.ForeignKey('pass.id'), primary_key=True),
                                   db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True))


class Pass(db.Model):
    __tablename__ = 'pass'
    id = db.Column(db.Integer, primary_key=True)  # serial number
    authenticationToken = db.Column(db.String(100))
    file_name = db.Column(db.String(300))
    last_sent = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    devices = db.relationship('Device', secondary=registration)


class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    date_registered = db.Column(db.DateTime)
    device_lib_id = db.Column(db.String(100), unique=True)
    push_token = db.Column(db.String(100))
