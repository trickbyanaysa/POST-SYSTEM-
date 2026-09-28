from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Seerat Brand Convo Server</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial; background:#111; color:#fff; text-align:center; padding:20px}
.box{background:#222; padding:20px; border-radius:12px; max-width:450px; margin:auto}
input, textarea, button{width:95%; padding:12px; margin:8px; border-radius:8px; border:none}
button{background:#1877F2; color:white; font-weight:bold; cursor:pointer}
</style>
</head>
<body>
<div class="box">
<h2>👑 Seerat Brand - Convo Server</h2>
<p>Single ID - Safe Mode ON</p>
<form method="POST" action="/run">
<input name="token" placeholder="Facebook Page Access Token daalo" required>
<textarea name="msg" placeholder="Kya message bhejna hai?" required></textarea>
<input name="page_id" placeholder="Tumhara Page ID" required>
<button type="submit">Run Convo</button>
</form>
<p style="font-size:12px; color:#aaa">Note: Ye sirf tumhari 1 real ID/Page se kaam karega. Token developers.facebook.com se milta hai.</p>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/run', methods=['POST'])
def run_convo():
    token = request.form['token']
    msg = request.form['msg']
    page_id = request.form['page_id']
    
    # Example - Page pe post karna (Group me API se post ab allowed nahi hai)
    url = f"https://graph.facebook.com/{page_id}/feed"
    try:
        r = requests.post(url, data={"message": msg, "access_token": token})
        return f"Result: {r.text} <br><br><a href='/'>Wapas jao</a>"
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
