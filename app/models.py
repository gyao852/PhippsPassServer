from app import db


member_card_association = db.Table('member_card_association', db.Model.metadata,
                                   db.Column('member_id', db.String(100), db.ForeignKey('member.id')),
                                   db.Column('card_id', db.Integer, db.ForeignKey('card.id')))


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
    cards = db.relationship('Card', secondary=member_card_association)

# don't know why, but association table created when added primary_key=True? even though no need for above
# TODO: changed from caad_id to card_id and psql broke; removing primary_key=True for now
registration = db.Table('card_device_association', db.Model.metadata,
                                   db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
                                   db.Column('device_id', db.Integer, db.ForeignKey('device.id')))


class Card(db.Model):
    __tablename__ = 'card'
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
