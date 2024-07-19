from datetime import timedelta
from flask import Flask
from extension.extension import db, cors, jwt
from routes import auth, user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/vitato'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static\\upload'
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)

db.init_app(app)
cors.init_app(app)
jwt.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
