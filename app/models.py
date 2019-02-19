from app import db
from sqlalchemy.dialects.postgresql import JSON

class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    member_level = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    associated_members = db.Column(db.String(100)) # May need to remove
    address_line_1 = db.Column(db.String(100), nullable=False)
    address_line_2 = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    passes = db.relationship('Pass', backref='member', lazy=True)

    def __init__(self, member_level, full_name, status, expiration_date,associated_members,
                    address_line_1,address_line_2,city,state,zip,email,passes=[]):
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

    def __repr__(self):
        return '<{}'.format(self.full_name)

class Pass(db.Model):
    __tablename__ = 'pass'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(300))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    active = db.Column(db.Boolean)
    last_sent = db.Column(db.DateTime)

    def __init__(self, file_name, active, member_id,last_sent):
        self.file_name = file_name
        self.member_id = member_id
        self.active = active
        self.last_sent = last_sent

    def __repr__(self):
        return '<id {}'.format(self.id)
