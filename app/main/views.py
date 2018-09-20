from datetime import datetime
from flask import render_template,session,redirect,url_for,request
from flask_login import current_user

from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/flaskindex')
def date():
    return render_template('index.html',current_time=datetime.utcnow())



@main.route('/some', methods = ['GET', 'POST'])
def some():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            print('in user is None')
            user = User(username=form.name.data)
            db.session.add(user)
            #                db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    if current_user.is_authenticated:
        name = current_user.username
    else:
        name = 'Strange'
    return render_template('some.html',
                           form=form, name=name,
                           known=session.get('known', False))


@main.route('/login', methods = ['GET', 'POST'])
def login():
    print('in mainlogin')
    if request.method == 'POST':
        if request.form['user'] == 'admin':
            return 'Admin login successfully!'
        else:
            return 'No such user!'
    title = request.args.get('user','Default')
    print(title)
    return render_template('login.html',title=title)

@main.route('/arg/<name>/<id>')
def arg(name,id):
    return 'good '+name +' '+ id

@main.route('/')
@main.route('/index')
def index():
    print('in spanic index')
    return render_template('spanic-index.html')

@main.route('/product')
def product():
    print('in spanic product')
    return render_template('spanic-product.html')