import webview
import threading
import os
from flask import Flask, render_template, url_for, redirect, flash, jsonify
from extensions import db
from models import Member
from forms import RegistrationForm, TransactionForm

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
    return render_template('transactions.html', TransactionForm=TransactionForm())

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members, RegistrationForm=RegistrationForm())

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')
    
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

@app.post('/transaction')
def transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        member = form.member.data
        deposit = form.deposit.data
        pay = form.pay.data
        if member:
            try:
                member.balance += deposit
                member.balance -= pay
                db.session.commit()
                print(f"{member.nickname} ({member.id}) blev afregnet.")
            except Exception as e:
                db.session.rollback()
                print(f'Fejl i transaktionen: {e}')
        else:
            print(f'Medlemsnummer {member.id} blev ikke fundet i databasen.')
    return redirect(url_for('transactions'))

@app.route('/member/<int:member_id>/balance')
def get_member_balance(member_id):
    member = db.session.get(Member, member_id)
    if member:
        return jsonify({'balance': member.balance})
    else:
        return jsonify({'error': 'Member not found'}), 404

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Barprogram", "http://127.0.0.1:5000", width=640, height=780)
    webview.start()