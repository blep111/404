from flask import Flask, request, redirect, send_from_directory
import requests, re, random, os

app = Flask(__name__, static_folder="public")

OWNER_FB = "https://www.facebook.com/profile.php?id=61582034805699"
APPROVAL_KEY = os.environ.get("APPROVAL_KEY", "404")

ua_list = [
    "Mozilla/5.0 (Linux; Android 10; Wildfire E Lite)...",
    "Mozilla/5.0 (Linux; Android 11; KINGKONG 5 Pro)...",
    "Mozilla/5.0 (Linux; Android 11; G91 Pro)..."
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
    except:
        return None


@app.route("/", methods=["GET"])
def index():
    return send_from_directory("public", "index.html")


@app.route("/verify", methods=["POST"])
def verify():
    key = request.form.get("key")
    if key == APPROVAL_KEY:
        return send_from_directory("public", "share.html")
    else:
        return f"""
        <html><head>
        <meta http-equiv='refresh' content='2;url={OWNER_FB}'>
        </head>
        <body style='background:black;color:#ff5555;text-align:center;padding-top:100px;font-family:Poppins,sans-serif;'>
        ❌ Wrong key! Redirecting to owner for approval...
        </body></html>
        """


@app.route("/share.html", methods=["GET"])
def block_direct_access():
    # Always redirect to key page unless form submission approved
    return redirect("/")


@app.route("/api/share", methods=["POST"])
def share():
    data = request.get_json()
    cookie = data.get("cookie")
    post_link = data.get("link")
    limit = int(data.get("limit", 0))

    if not cookie or not post_link or not limit:
        return "⚠️ Missing input."

    ua = random.choice(ua_list)
    token = extract_token(cookie, ua)
    if not token:
        return "❌ Token extraction failed."

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

    return f"✅ Successfully shared {success} time(s)."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)