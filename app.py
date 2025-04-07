import webview
import threading
import os
from flask import Flask, render_template, url_for, redirect, flash
from extensions import db
from models import Member
from forms import RegistrationForm, DepositForm

app = Flask(__name__, static_folder = 'static', template_folder = 'templates', instance_path = r'C:\Users\Bar\Desktop\Barprogram')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

with app.app_context():
    db.create_all()

def start_flask():
    app.run(debug=False, port=5000)

@app.route('/')
def index():
    return redirect('/transactions')

@app.route('/transactions')
def transactions():
    # new_member = Member(id=90110, nickname='Dexter')
    # db.session.add(new_member)
    # db.session.commit()
    return render_template('transactions.html', DepositForm=DepositForm())

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members, RegistrationForm=RegistrationForm())

# FORMULARER
@app.post('/register')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_member = Member(id=form.id.data, nickname=form.nickname.data, authorized=False) 
        try:
            db.session.add(new_member)
            db.session.commit()
            print('Ny bruger oprettet')
            flash(f'Ny bruger oprettet for {form.nickname.data}', 'success')
        except Exception as e:
            db.session.rollback()
            print('Fejl ved oprettelse')
            flash(f'Der var en fejl med at oprette brugeren.\n{e}', 'error')
    else:
        print('Fejl i registrering')
        flash('Registrering fejlede.')
    return redirect(url_for('members'))

@app.post('/member/delete/<member_id>')
def delete_member(member_id):
    member = db.session.get(Member, member_id)
    if member:
        try:
            db.session.delete(member)
            db.session.commit()
            print('Medlem slettet')
        except Exception as e:
            db.session.rollback()
            print(f'Fejl i sletning af medlem: {e}')
    else:
        print(f'Medlemsnummer {member_id} blev ikke fundet i databasen.')
    return redirect(url_for('members'))

@app.post('/deposit')
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        member = form.member.data
        amount = form.amount.data
        if member:
            try:
                member.balance += abs(amount)
                db.session.commit()
                print(f"Tilføjede {amount} kroner på {member.nickname} ({member.id})s barkonto.")
            except Exception as e:
                db.session.rollback()
                print(f'Fejl i transaktionen: {e}')
        else:
            print(f'Medlemsnummer {member.id} blev ikke fundet i databasen.')
    return redirect(url_for('members'))

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Barprogram", "http://127.0.0.1:5000")
    webview.start()