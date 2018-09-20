
from flask import render_template,session,redirect,url_for,request,flash,current_app
from flask_login import login_user,logout_user, login_required, current_user
from . import auth
from ..models import  User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .. import db
from ..email import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('wellcome: %s'%current_user.username)
            return redirect(request.args.get('next') or url_for('main.some'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.some'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been send to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        flash("The confirmation link is invalid or has expired.")
        return redirect(url_for('main.some'))
    id = data.get('confirm')
    user = User.query.filter_by(id=id).first_or_404()

    if user.confirmed:
        return redirect(url_for('main.some'))
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash("You have confirm your account. Thanks!")

    return redirect(url_for('main.some'))
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.'\
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.some'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user,token=token)
    flash('A new confirmation email has been send to you by email.')
    return redirect(url_for('main.some'))

@auth.route('/change_password',methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('main.some'))
        else:
            flash("Invalid old password, please re-input")
    return render_template('auth/change_password.html', form=form)

@auth.route('/secret')
@login_required
def secret():
    flash("in secret and then out")
    return "Only authenticated users are allowed"

