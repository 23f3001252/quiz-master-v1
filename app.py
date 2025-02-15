from flask import Flask, render_template, request, redirect, url_for, session

from application.models import * 

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'adsfdf24247vf_343jwowqqe'
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controllers import * 




if __name__ == "__main__":
    app.run(debug=True)

