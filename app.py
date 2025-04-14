import webview
import threading
import os
from flask import Flask, render_template, url_for, redirect, flash, jsonify
from flask_babel import Babel, format_datetime
from extensions import db
from models import Member, Transaction
from forms import RegistrationForm, TransactionForm

app = Flask(__name__, static_folder = 'static', template_folder = 'templates', instance_path = r'C:\Users\Bar\Desktop\Barprogram')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['BABEL_DEFAULT_LOCALE'] = 'da_DK'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Copenhagen'
app.jinja_env.globals['format_datetime'] = format_datetime
babel = Babel(app)
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

@app.route('/transactions/<member_id>')
def member_transaction(member_id):
    member = db.session.get(Member, member_id)
    form = TransactionForm()
    if member:
        form.member.data = member
    return render_template('transactions.html', TransactionForm=form, member=member)

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/sales')
def sales():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('sales.html', transactions=transactions)

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

@app.get('/member/<member_id>')
def member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.get('/create_member')
def create_member():
    return render_template('create_member.html', RegistrationForm=RegistrationForm())

@app.get('/edit_member/<member_id>')
def edit_member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.get('/authorize_member/<member_id>')
def authorize_member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('authorize_member.html', member=member)

@app.get('/delete_member/<member_id>')
def delete_member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.get('/member_history/<member_id>')
def member_history(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.get('/shared_account/<member_id>')
def shared_account(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.post('/member/delete/<member_id>')
def delete_member_old(member_id):
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
                transaction = Transaction(member_id=member.id, deposit=deposit, pay=pay)
                db.session.add(transaction)
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
        return jsonify({'error': f'Medlemsnummer {member.id} blev ikke fundet i databasen.'}), 404

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Barprogram", "http://127.0.0.1:5000", width=640, height=780)
    webview.start()