from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__, static_folder="public", template_folder="public")

# CHANGE THESE:
APPROVED_KEY = "xren-404"
OWNER_URL = "https://facebook.com/your.profile"  # <-- your real FB account
API_URL = "https://your-working-autoshare-api.com/share"  # your API

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        key = request.form.get("key")
        if key == APPROVED_KEY:
            return redirect(url_for("share_page"))
        else:
            return redirect(f"{OWNER_URL}?message=Please%20message%20the%20creator%20for%20an%20access%20key.")
    return render_template("index.html")

@app.route("/share", methods=["GET", "POST"])
def share_page():
    if request.method == "POST":
        post_url = request.form.get("post_url")
        amount = request.form.get("amount")

        try:
            r = requests.get(f"{API_URL}?post={post_url}&amount={amount}")
            data = r.json()
            status = data.get("status", "error")
            message = data.get("message", "No response")
            shares = data.get("shared_count", "0")

            if status == "success":
                return render_template(
                    "share.html",
                    success=True,
                    message=f"✅ {message}",
                    shares=shares,
                )
            else:
                return render_template(
                    "share.html",
                    success=False,
                    message=f"❌ {message}",
                )
        except Exception as e:
            return render_template("share.html", success=False, message=str(e))

    return render_template("share.html", success=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))