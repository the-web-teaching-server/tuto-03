from flask import Flask, render_template
import os
import base64

app = Flask(__name__)

SHORTCUTS = {
  'EbA356Ak': "http://www.example.com",
  'aoM4apKh': "http://www.mozilla.org",
}

@app.route("/")
def hello():
  return render_template('index.html', shortcuts_count=len(SHORTCUTS))
 
def generate_new_key():
  key = base64.urlsafe_b64encode(os.urandom(6)).decode()
  while key in SHORTCUTS:
    key = base64.urlsafe_b64encode(os.urandom(6)).decode()
  return key

@app.route("/demo/<username>")
def demo(username):
  return username
  return render_template("demo.html", username=username)


if __name__ == '__main__':
    app.run(debug=True)
