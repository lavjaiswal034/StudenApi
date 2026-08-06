from flask import Flask
from routes.student import student
from config import Config
from extensions import db, jwt
from models import User, Student
from routes.auth import auth
from flasgger import Swagger

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

Swagger(app)

app.register_blueprint(auth)
app.register_blueprint(student)

print("\n========== REGISTERED ROUTES ==========")

for rule in app.url_map.iter_rules():
    print(rule)

print("=======================================\n")
@app.route("/")
def home():
    return {"message": "Student API is Live 🚀"}



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)