from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Regexp
from models import Member
from extensions import db


class RegistrationForm(FlaskForm):
    id = StringField('Medlemsnummer', validators=[DataRequired(), Regexp(r'^90+(?:\d{2}|[1-9]\d{2})', message="Medlemsnummeret er ugyldigt.")])
    nickname = StringField('Navn', validators=[DataRequired(), Length(min=2, max=32)])
    # pincode = PasswordField('Pinkode', validators=[Regexp(r'^\d{4}$', message="Pinkode skal være fire cifre.")])
    submit = SubmitField('Opret')

def member_label(member):
    return f'({member.id}) {member.nickname}'

class DepositForm(FlaskForm):
    member = QuerySelectField('Medlem',
    validators=[DataRequired()],
    query_factory=lambda: db.session.execute(db.select(Member).order_by(Member.id)).scalars(),
    get_label=member_label,
    allow_blank=True,
    blank_text='-- Vælg et medlem --'
    )
    amount = IntegerField('Beløb', validators=[DataRequired()])
    submit = SubmitField('Indsæt')
