from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import boto3, botocore
import os, secrets, json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/database.db"
db = SQLAlchemy(app)

s3 = boto3.client(
   "s3",
   aws_access_key_id="AKIAZ3GCPRHWA3OXZ4NE",
   aws_secret_access_key="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"
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    model_url = db.Column(db.String(80))
    script_url = db.Column(db.String(80))
    config = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    return os.getcwd()

@app.route("/jtguibas/<model_url>", methods=["GET"])
def render(model_url):
    return render_template(model_url + ".html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        data = request.json
        prime = User(username=data["username"], password=data["password"])
        prime.api_key = secrets.token_hex(5)
        db.session.add(prime)
        db.session.commit()
        return prime.api_key
        
@app.route("/api/v1/falcon_submit", methods=["POST"])
def falcon_submit():
    data = request.json
    prime = User.query.filter_by(api_key=data["api_key"]).first()
    
    input_type = data["input"].split(".")[0]
    output_type = data["output"].split(".")[0]
    input_shape = data["input"].split(".")[1].split("x")
    output_shape = data["output"].split(".")[1].split("x")
    
    config = {
        "model_url": data["model_url"],
        "code_url": data["model_url"],
        "input_type": input_type,
        "input_channels": input_shape[0],
        "input_width": input_shape[1],
        "input_height": input_shape[2],
        "output_type": output_type,
        "output_channels": input_shape[0],
        "output_width": input_shape[1],
        "output_height": input_shape[2],
    }

    with open("storage/" + data["api_key"] + ".json", 'w') as fp:
        json.dump(config, fp)

    return "Request Accepted. Is it correct? Who knows."


if __name__ == '__main__':
    app.run(debug=True)
    