from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, PasswordField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Optional, Length, Regexp, NumberRange
from models import Member
from extensions import db

def member_label(member):
    return f'{member.id} {member.nickname}'

class RegistrationForm(FlaskForm):
    id = StringField('Medlemsnummer', validators=[DataRequired(), Regexp(r'^90+(?:\d{2}|[1-9]\d{2})', message="Medlemsnummeret er ugyldigt.")])
    nickname = StringField('Navn', validators=[DataRequired(), Length(min=2, max=32)])
    submit = SubmitField('Opret')

class EditMemberForm(FlaskForm):
    id = StringField('Medlemsnummer', validators=[DataRequired(), Regexp(r'^90+(?:\d{2}|[1-9]\d{2})', message="Medlemsnummeret er ugyldigt.")])
    nickname = StringField('Navn', validators=[DataRequired(), Length(min=2, max=32)])
    submit = SubmitField('Ændr medlem')

class CreateSharedAccountForm(FlaskForm):
    member_a = QuerySelectField('Medlem A',
        validators=[DataRequired()],
        # TODO: Lav rigtig query factory (alle medlemmer uden fælleskonto)
        query_factory=lambda: db.session.execute(db.select(Member).order_by(Member.id)).scalars(),
        get_label=member_label,
        allow_blank=False)
    member_b = QuerySelectField('Medlem B',
        validators=[DataRequired()],
        # TODO: Lav rigtig query factory (alle medlemmer uden fælleskonto der ikke er medlem A)
        query_factory=lambda: db.session.execute(db.select(Member).order_by(Member.id)).scalars(),
        get_label=member_label,
        allow_blank=False)
    submit = SubmitField('Opret fælleskonto')
    
class TransactionForm(FlaskForm):
    member = QuerySelectField('Medlem',
    validators=[DataRequired()],
    query_factory=lambda: db.session.execute(db.select(Member).order_by(Member.id)).scalars(),
    get_label=member_label,
    allow_blank=False
    )
    deposit = IntegerField('Indsæt', default=0, render_kw={'step': 5}, validators=[Optional(), NumberRange(min=0, message="Beløbet skal være positivt.")])
    pay = IntegerField('Betal', default=0, render_kw={'step': 5}, validators=[Optional(), NumberRange(min=0, message="Beløbet skal være positivt.")])
    submit = SubmitField('Gennemfør')

class LoginForm(FlaskForm):
    member = QuerySelectField('Barvagt',
    validators=[DataRequired()],
    query_factory=lambda: db.session.execute(db.select(Member).filter_by(authorized=True).order_by(Member.id)).scalars(),
    get_label=member_label,
    allow_blank=False
    )
    pincode = PasswordField('Pinkode', validators=[DataRequired()])
    submit = SubmitField('Log ind')
    
class ChangePincodeForm(FlaskForm):
        current_pincode = StringField('Nuværende pinkode', validators=[DataRequired()])
        new_pincode = StringField('Ny pinkode', validators=[DataRequired()])
        submit = SubmitField('Skift pinkode')