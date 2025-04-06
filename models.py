from extensions import db

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nickname = db.Column(db.String(32), unique=True, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    pin_code = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f"Member('{self.id}', '{self.nickname}')"