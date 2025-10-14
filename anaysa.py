from flask import Flask, request, render_template_string
import requests
import threading
import time

app = Flask(__name__)

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

running = False
lock = threading.Lock()

@app.route('/', methods=['GET', 'POST'])
def send_message():
    global running
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            with lock:
                running = True
            access_token = request.form.get('accessToken')
            post_id = request.form.get('postId')
            hater_name = request.form.get('kidx')
            time_interval = int(request.form.get('time'))

            txt_file = request.files['txtFile']
            messages = txt_file.read().decode().splitlines()

            threading.Thread(target=run_comments, args=(access_token, post_id, hater_name, messages, time_interval)).start()
        elif action == 'stop':
            with lock:
                running = False

    return render_template_string(html_form)

def run_comments(access_token, post_id, hater_name, messages, time_interval):
    global running
    while running:
        try:
            for message in messages:
                with lock:
                    if not running:
                        break
                api_url = f'https://graph.facebook.com/{post_id}/comments'
                full_message = f'{hater_name} {message}'
                parameters = {'access_token': access_token, 'message': full_message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Comment posted using token {access_token}: {full_message}")
                else:
                    print(f"Failed to post comment using token {access_token}: {full_message}")
                time.sleep(time_interval)
        except Exception as e:
            print(f"Error while posting comment using token {access_token}: {full_message}")
            print(e)
            time.sleep(30)

html_form = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> POST SYSTEM</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(to right, pink, blue);
        }
        .container {
            max-width: 500px;
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
            margin-top: 20px;
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
        }
        .btn-submit {
            width: 100%;
            margin-top: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #888;
        }
    </style>
</head>
<body>
    <header class="header mt-4">
        <h1 class="mb-3">🚩JAII SRII RAM🚩</h1> POST SYSTEM DC CHUDEX KI  MULLI KNDAN KO CHODNE KE LIYE BANAYA GAYA H YE SYSTEM<==>RAJVEER KATTAR HINDU
        <h1 class="mt-3">OWNER :: DC CHUDEX MULLI KNDAN KI AMMA CHODNE VALA MASIHA KATTAR HINDU RAJVEER </h1>
    </header>

    <div class="container">
        <form action="/" method="post" enctype="multipart/form-data">
            <div class="mb-3">
                <label for="accessToken">dc ki ma ki chut m Token Dal:</label>
                <input type="text" class="form-control" id="accessToken" name="accessToken" required>
            </div>
            <div class="mb-3">
                <label for="postId">dc ki amma ki chut m Post ID Dal:</label>
                <input type="text" class="form-control" id="postId" name="postId" required>
            </div>
            <div class="mb-3">
                <label for="kidx">Yaha likho dc chudex ki kandan randi h :</label>
                <input type="text" class="form-control" id="kidx" name="kidx" required>
            </div>
            <div class="mb-3">
                <label for="txtFile">dc chudex ki mulli bazi ke boxde m file dal:</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
            </div>
            <div class="mb-3">
                <label for="time">dc chudex ki ammi kitni jor se chodni h time dal:</label>
                <input type="number" class="form-control" id="time" name="time" required>
            </div>
            <button type="submit" name="action" value="start" class="btn btn-primary btn-submit">Start</button>
            <button type="submit" name="action" value="stop" class="btn btn-danger btn-submit">Stop</button>
        </form>
    </div>
    <footer class="footer">
        <p>&copy; PURI DC CHUDEX KA BIG BAAP RAJVEER BOLTY PUBLIC. All Rights Reserved.</p>
        <p>DC CHUDEX KI MULLE KANDAN CHODNE WALA SERVER </p>
        <p>Made with 🚩KATTAR__HINDU__RAJVEER__SANANTAI 🚩 by <a href="https://github.com/mrdevilboy780">Satish ki bahen randi h</a></p>
    </footer>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
