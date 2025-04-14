from extensions import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nickname = db.Column(db.String(32), unique=True, nullable=False)
    pincode = db.Column(db.String(256), nullable=True)
    authorized = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Integer(), nullable=False, default=0)

    # Relationships
    transactions = db.relationship("Transaction", backref="member", lazy=True)

    # Methods
    def set_pincode(self, pincode):
        self.pincode = generate_password_hash(pincode)

    def check_pincode(self, pincode):
        return check_password_hash(self.pincode, pincode)

    def __repr__(self):
        return f"<Medlem {self.nickname}>"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    deposit = db.Column(db.Integer, nullable=False, default=0)
    pay = db.Column(db.Integer, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)

class SharedAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_a = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    member_b = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

class Privilege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sharer = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
