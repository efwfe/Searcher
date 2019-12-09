import settings
import os
from flask import Flask, session, redirect, url_for, request, render_template
from views.home import home
from views.user import user

app = Flask(__name__)
app.config.from_object(settings.DevelopmentConfig)
app.secret_key = os.urandom(24)
app.register_blueprint(home, url_prefix='/supervisor')
app.register_blueprint(user, url_prefix='/supervisor')


@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.before_request
def login_interceptor():
    path = request.path
    if path.startswith("/supervisor"):
        if path == '/supervisor/login.html' or path == '/supervisor/login':
            return
        if not 'is_login' in session or not session['is_login']:
            return redirect(url_for('user.login'))

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
