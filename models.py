from extensions import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nickname = db.Column(db.String(32), unique=True, nullable=False)
    pincode = db.Column(db.String(256), nullable=True)
    authorized = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Integer(), nullable=False, default=0)

    # Relationships
    transactions = db.relationship("Transaction", backref="member", lazy=True, cascade="all, delete-orphan")

    # Methods
    def set_pincode(self, pincode):
        self.pincode = generate_password_hash(pincode)

    def check_pincode(self, pincode):
        if self.pincode is None:
            return False
        return check_password_hash(self.pincode, pincode)

    def __repr__(self):
        return f"<Medlem {self.nickname}>"
    
    shared_as_a = db.relationship(
        "SharedAccount",
        foreign_keys="[SharedAccount.member_a_id]",
        back_populates="member_a",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    shared_as_b = db.relationship(
        "SharedAccount",
        foreign_keys="[SharedAccount.member_b_id]",
        back_populates="member_b",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    @property
    def is_shared(self):
        """True if this member appears in any SharedAccount (as A or B)."""
        return (
            self.shared_as_a.count() > 0 or
            self.shared_as_b.count() > 0
        )
        
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'), nullable=False)
    deposit = db.Column(db.Integer, nullable=False, default=0)
    pay = db.Column(db.Integer, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)
    authorizer = db.Column(db.String(32), nullable=False)

class SharedAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_a = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    member_b = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    balance = db.Column(db.Integer(), nullable=False, default=0)
    

class Privilege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sharer = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
