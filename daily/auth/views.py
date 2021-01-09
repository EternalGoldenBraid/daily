from daily.models import User
from daily.auth.forms import LoginForm
from flask import (render_template, redirect, flash,
        url_for, request)
from flask_login import (current_user, login_user,
                    logout_user, login_required)
from werkzeug.urls import url_parse
from daily.auth import bp



@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Logs user in
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
    # Check if request was a POST request
        # Attempt to fetch users username from the database, 
        # take the first result
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        # Forward to the page the attempted to get at before authentication
        if not next_page or url_parse(next_page) != '':
            return redirect(url_for('main.index'))

        return redirect(next_page)

    return render_template('auth/login.html', title='Log In', form=form)

# url_parse() Parses a URL from a string into a URL tuple.
#If the URL is lacking a scheme it can be provided as second argument.
#Otherwise, it is ignored. Optionally fragments can be stripped from
#the URL by setting allow_fragments to False.
#The inverse of this function is url_unparse().

@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers user 
    """

    # Awaiting rating table modification for multi user support
    return url_for('auth.register')

        #if form.password != form.password_confimation:
        #    flash("Passwords don't match")
        #    return redirect(url_for('auth.register'))
    
        #if current_user.is_authenticated:
        #    return redirect(url_for('main.index'))
        #form = RegisterForm()
        #if form.validate_on_submit():         
        ## Check if request was a POST request 
    
        #    # Check if user already exists
        #    username = form.username.data
        #    user = User.query.filter_by(username=username).first()
    
        #    if user is not None:
        #        flash('Username already exists')
        #        return redirect(url_for('auth.register'))
    
        #    # Create user
        #    u = User(username=username, email=#TODO)
        #    u.set_password(form.password.data)
    
        #    login_user(user, remember=form.remember_me.data)
        #    next_page = request.args.get('next')
        #    
        #    # Forward to the page the attempted to get at before authentication
        #    if not next_page or url_parse(next_page) != '':
        #        return redirect(url_for('main.index'))
    
        #    return redirect(next_page)
    
        #return render_template('login.html', title='Log In', form=form)


# Route for loggine the user out
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
