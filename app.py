from flask import Flask, redirect, request, session, render_template, url_for
import requests
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "YOUR_CLIENT_KEY")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

SCOPE = "user.info.basic,video.publish,video.upload"
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)


@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    params = (
        f"?client_key={CLIENT_KEY}"
        f"&scope={SCOPE}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )
    return redirect(AUTH_URL + params)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if state != session.get("oauth_state"):
        return "State mismatch error", 400

    resp = requests.post(TOKEN_URL, data={
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    })
    token_data = resp.json().get("data", {})
    session["access_token"] = token_data.get("access_token")
    session["user"] = {"open_id": token_data.get("open_id")}
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/demo-login")
def demo_login():
    session["access_token"] = "demo_token"
    session["user"] = {"open_id": "demo_user_12345", "display_name": "My TikTok Account"}
    return redirect(url_for("index"))


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True)
