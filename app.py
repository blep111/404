from flask import Flask, request, jsonify, redirect, url_for, session, send_from_directory
import requests, re, random, os

app = Flask(__name__, static_folder="public")
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

OWNER_FB = "https://www.facebook.com/profile.php?id=61582034805699"
APPROVAL_KEY = os.environ.get("APPROVAL_KEY", "404")

ua_list = [
    "Mozilla/5.0 (Linux; Android 10; Wildfire E Lite) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.136 Mobile Safari/537.36[FBAN/EMA;FBLC/en_US;FBAV/298.0.0.10.115;]",
    "Mozilla/5.0 (Linux; Android 11; KINGKONG 5 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36[FBAN/EMA;FBLC/fr_FR;FBAV/320.0.0.12.108;]",
    "Mozilla/5.0 (Linux; Android 11; G91 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/106.0.5249.126 Mobile Safari/537.36[FBAN/EMA;FBLC/fr_FR;FBAV/325.0.1.4.108;]"
]

def extract_token(cookie, ua):
    try:
        cookies = {i.split('=')[0]: i.split('=')[1] for i in cookie.split('; ') if '=' in i}
        res = requests.get("https://business.facebook.com/business_locations", headers={
            "user-agent": ua,
            "referer": "https://www.facebook.com/"
        }, cookies=cookies)
        token_match = re.search(r'(EAAG\w+)', res.text)
        return token_match.group(1) if token_match else None
    except Exception as e:
        print("Token extraction error:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            key = request.form.get("key")
            if key == APPROVAL_KEY:
                session["approved"] = True
                return redirect(url_for("share_page"))
            else:
                return f'''
                <html>
                    <head>
                        <meta http-equiv="refresh" content="1;url={OWNER_FB}">
                    </head>
                    <body style="background:black;color:#ff6b6b;text-align:center;padding-top:100px;font-family:Poppins,Arial,sans-serif;">
                        ❌ Invalid key. Redirecting to owner...
                    </body>
                </html>
                '''
        return send_from_directory("public", "index.html")
    except Exception as e:
        return f"Error on index page: {e}"

@app.route("/share", methods=["GET"])
def share_page():
    if not session.get("approved"):
        return redirect(url_for("index"))
    return send_from_directory("public", "share.html")

@app.route("/api/share", methods=["POST"])
def share():
    if not session.get("approved"):
        return jsonify({"status": False, "message": "Key not approved."})
    try:
        data = request.get_json()
        cookie = data.get("cookie")
        post_link = data.get("link")
        limit = int(data.get("limit", 0))
        if not cookie or not post_link or not limit:
            return jsonify({"status": False, "message": "Missing input."})

        ua = random.choice(ua_list)
        token = extract_token(cookie, ua)
        if not token:
            return jsonify({"status": False, "message": "Token extraction failed."})

        cookies = {i.split('=')[0]: i.split('=')[1] for i in cookie.split('; ') if '=' in i}
        success = 0
        for _ in range(limit):
            res = requests.post(
                "https://graph.facebook.com/v18.0/me/feed",
                params={"link": post_link, "access_token": token, "published": 0},
                headers={"user-agent": ua},
                cookies=cookies
            )
            if "id" in res.text:
                success += 1
            else:
                break

        return jsonify({
            "status": True,
            "message": f"✅ Shared {success} times.",
            "success_count": success
        })
    except Exception as e:
        return jsonify({"status": False, "message": f"Error: {e}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)