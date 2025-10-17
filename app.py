from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__, static_folder="public", template_folder="public")

OWNER_URL = "https://facebook.com/your.owner.profile"  # change this
API_URL = "https://your-real-autoshare-api.com/share"
APPROVED_KEY = "mysecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        key = request.form.get("key")
        if key == APPROVED_KEY:
            return redirect(url_for("share_page"))
        else:
            return redirect(OWNER_URL)
    return render_template("index.html")

@app.route("/share", methods=["GET", "POST"])
def share_page():
    if request.method == "POST":
        post_url = request.form.get("post_url")
        amount = request.form.get("amount")
        try:
            r = requests.get(f"{API_URL}?post={post_url}&amount={amount}")
            data = r.json()
            if data.get("status") == "success":
                return render_template(
                    "share.html",
                    success=True,
                    message="✅ Share successful!",
                    shares=data.get("shared_count", "N/A"),
                )
            else:
                return render_template(
                    "share.html",
                    success=False,
                    message=f"❌ {data.get('message', 'Unknown error')}",
                )
        except Exception as e:
            return render_template("share.html", success=False, message=str(e))
    return render_template("share.html", success=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))