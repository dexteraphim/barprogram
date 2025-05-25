import os
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request, abort
from flask_babel import Babel, format_datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from flask_wtf import FlaskForm
from extensions import db
from models import Member, Transaction, SharedAccount
from forms import RegistrationForm, EditMemberForm, TransactionForm, LoginForm, ChangePincodeForm, CreateSharedAccountForm

app = Flask(__name__, static_folder = 'static', template_folder = 'templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['BABEL_DEFAULT_LOCALE'] = 'da_DK'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Copenhagen'
app.jinja_env.globals['format_datetime'] = format_datetime
babel = Babel(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(member_id):
    return db.session.get(Member, member_id)

def authorized_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.authorized:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function

with app.app_context():
    db.create_all()

def start_flask():
    app.run(debug=False, port=5000)

### Routes
@app.get('/')
@login_required
def index():
    return redirect('/transactions')

@app.get('/transactions')
@login_required
def transactions():
    return render_template('transactions.html', TransactionForm=TransactionForm())

@app.get('/transactions/<member_id>')
def member_transaction(member_id):
    member = db.session.get(Member, member_id)
    form = TransactionForm()
    if member:
        form.member.data = member
    return render_template('transactions.html', TransactionForm=form, member=member)

@app.post('/transaction')
def process_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        member = form.member.data
        deposit = form.deposit.data
        pay = form.pay.data
        if member:
            try:
                member.balance += deposit
                member.balance -= pay
                transaction = Transaction(member_id=member.id, deposit=deposit, pay=pay, authorizer=f'{current_user.id} {current_user.nickname}')
                db.session.add(transaction)
                db.session.commit()
                print(f"{member.nickname} ({member.id}) blev afregnet.")
            except Exception as e:
                db.session.rollback()
                print(f'Fejl i transaktionen: {e}')
        else:
            print(f'Medlemsnummer {member.id} blev ikke fundet i databasen.')
    return redirect(url_for('member_transaction', member_id=member.id))

@app.get('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.get('/sales')
def sales():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('sales.html', transactions=transactions)

@app.get('/settings')
def settings():
    return render_template('settings.html', ChangePincodeForm=ChangePincodeForm())

### Member GET
@app.get('/member/<member_id>')
def member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('member.html', member=member)

@app.get('/member/create')
def create_member():
    return render_template('create_member.html', RegistrationForm=RegistrationForm())

@app.get('/member/<member_id>/edit')
def get_edit_member(member_id):
    member = db.session.get(Member, member_id)
    return render_template('edit_member.html', member=member, EditMemberForm=EditMemberForm())

@app.get('/member/<member_id>/shared')
def get_shared_account(member_id):
    member = db.session.get(Member, member_id)
    form = CreateSharedAccountForm()
    form.member_a.data = member
    return render_template('create_shared_account.html', CreateSharedAccountForm=form, member=member)

@app.get('/member/<int:member_id>/balance')
def get_member_balance(member_id):
    member = db.session.get(Member, member_id)
    if member:
        return jsonify({'balance': member.balance})
    else:
        return jsonify({'error': f'Medlemsnummer {member.id} blev ikke fundet i databasen.'}), 404

### Member POST
@app.post('/member/create')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_member = Member(id=form.id.data, nickname=form.nickname.data, authorized=False) 
        try:
            db.session.add(new_member)
            db.session.commit()
            flash(f'Ny bruger oprettet for {form.nickname.data}', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Der var en fejl med at oprette medlemmet.\n{e}', 'error')
    else:
        flash('Registrering fejlede.')
    return redirect(url_for('members'))

@app.post('/member/<member_id>/edit')
def edit_member(member_id):
    form = EditMemberForm()
    if form.validate_on_submit():
        member = db.session.get(Member, member_id)
        try:
            member.id = form.id.data
            member.nickname = form.nickname.data
            db.session.commit()
            flash(f'Medlemmet blev ændret', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Der var en fejl med at ændre medlemmet.\n{e}', 'error')
    else:
        flash('Medlemsændring fejlede.')
    return redirect(url_for('members'))

@app.post('/member/<member_id>/delete')
def delete_member(member_id):
    member = db.session.get(Member, member_id)
    if member:
        try:
            db.session.delete(member)
            db.session.commit()
            print('Medlem slettet')
        except Exception as e:
            db.session.rollback()
            print(f'Exception: {e}')
    else:
        flash(f'Medlemsnummer {member_id} blev ikke fundet i databasen.', 'error')
        print('Medlem ikke fundet')
    return redirect(url_for('members'))

@app.post('/member/<member_id>/deauthorize')
def deauthorize_member(member_id):
    member = db.session.get(Member, member_id)
    if member and member.authorized == True:
        try:
            member.authorized = False
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Der var en fejl med at fjerne barvagt-rollen for medlemmet.\n{e}', 'error')
    else:
        flash(f'Medlemsnummer {member_id} blev ikke fundet i databasen.', 'error')
    return redirect(request.referrer)

@app.post('/member/<member_id>/authorize')
def authorize_member(member_id):
    member = db.session.get(Member, member_id)
    if member and member.authorized == False:
        try:
            member.authorized = True
            if member.pincode == None:
                member.set_pincode('1234')
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f'Der var en fejl med at tilføje barvagt-rollen for medlemmet.\n{e}', 'error')
    else:
        print(f'Medlemsnummer {member_id} blev ikke fundet i databasen.', 'error')
    return redirect(request.referrer)

# Shared account
@app.post('/shared/create')
def create_shared_account():
    form = CreateSharedAccountForm()
    if form.validate_on_submit():
        member_a = form.member_a.data
        member_b = form.member_b.data
        print(f'{member_a.nickname} nickname #1')
        
        account = SharedAccount(member_a=member_a.id, member_b=member_b.id, balance=(member_a.balance+member_b.balance))
        member_a.balance = account.balance
        member_b.balance = account.balance
        try:
            db.session.add(account)
            db.session.commit()
            flash(f'Ny fælleskonto oprettet for {form.member_a.data.id} {form.member_a.data.nickname} og {form.member_b.data.id} {form.member_b.data.nickname} ', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Der var en fejl med at oprette fælleskontoen.\n{e}', 'error')
            print(f'Error:\n{e}')
    else:
        flash('Registrering fejlede.')
        print('Validation error')
    return redirect(url_for('members'))

@app.post('/member/<int:member_id>/shared/delete')
def delete_shared_account(member_id):
    """Delete shared account for a specific member"""
    member = db.session.get(Member, member_id)
    if not member:
        flash(f'Medlemsnummer {member_id} blev ikke fundet i databasen.', 'error')
        return redirect(url_for('members'))
    
    # Find shared account where this member is either member_a or member_b
    shared_account = SharedAccount.query.filter(
        (SharedAccount.member_a == member_id) | 
        (SharedAccount.member_b == member_id)
    ).first()
    
    if shared_account:
        try:
            # Get the other member in the shared account
            other_member_id = shared_account.member_b if shared_account.member_a == member_id else shared_account.member_a
            other_member = db.session.get(Member, other_member_id)
            
            # Split the shared balance between the two members
            if other_member:
                split_balance = shared_account.balance // 2
                member.balance = split_balance
                other_member.balance = split_balance
            else:
                # If other member doesn't exist, give all balance to current member
                member.balance = shared_account.balance
            
            # Delete the shared account
            db.session.delete(shared_account)
            db.session.commit()
            
            flash(f'Fælleskonto slettet for {member.nickname}', 'success')
            print(f'Shared account deleted for member {member_id}')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Der var en fejl med at slette fælleskontoen.\n{e}', 'error')
            print(f'Error deleting shared account: {e}')
    else:
        flash(f'Ingen fælleskonto fundet for {member.nickname}', 'warning')
    
    return redirect(url_for('member', member_id=member_id))

# Authorization routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        member = form.member.data
        if member and member.check_pincode(form.pincode.data):
            if member.authorized:
                login_user(member)
                return redirect(url_for('transactions'))
            else:
                flash('You are not authorized to login.', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', LoginForm=form)

@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html', title = 'Protected')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_pincode/<int:member_id>', methods=['POST'])
def change_pincode(member_id):
    form = ChangePincodeForm()
    print(f"Form data: {form.data}")  # Print the form data
    print(f"Form errors: {form.errors}") # Print form errors
    if form.validate_on_submit():
        member = db.session.get(Member, member_id)
        if member and current_user.id == member.id and member.check_pincode(form.current_pincode.data):
            try:
                member.set_pincode(str(form.new_pincode.data))
                db.session.commit()
                print('Pinkoden er ændret.', 'success')
            except Exception as e:
                db.session.rollback()
                print(f'Der var en fejl med at skifte pinkoden: {e}', 'error')
        else:
            print('Forkert pinkode.', 'error')
    else:
        print('Validation failed')
    return redirect(request.referrer)
            
    
### Start app
if __name__ == '__main__':
    app.run(debug=True)