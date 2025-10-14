# save as app.py and run: python app.py
from flask import Flask, request, render_template_string, jsonify
import requests
import time
import threading
import uuid

app = Flask(__name__)

# ------------------------
# In-memory task store
# tasks = {
#   task_id: {
#       "thread": Thread,
#       "stop_event": threading.Event(),
#       "owner_token": "<token_or_owner_key>",
#       "post_id": "...",
#       "messages": [...],
#       "delay": N,
#       "logs": [...],
#       "status": "running" / "stopped" / "finished" / "error"
#   }
# }
# ------------------------
tasks = {}

# ------------------------
# HTML (UI) - skyblue + pink mix background, styled buttons/textareas
# ------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>SEERAT POST BOT - Updated</title>
<link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg1: #87CEEB;
    --bg2: #FFB6C1;
    --card: rgba(255,255,255,0.95);
    --accent: linear-gradient(45deg,#FF6B35,#FF8E53);
    --btn-text: #ffffff;
    --textarea-bg: #fff7fb;
    --muted: #2C3E50;
  }
  *{box-sizing:border-box;font-family: 'Ubuntu', sans-serif;}
  body{
    margin:0;
    min-height:100vh;
    background: radial-gradient(circle at 10% 10%, rgba(255,182,193,0.25), transparent 10%),
                linear-gradient(135deg,var(--bg1),var(--bg2));
    padding:30px;
    display:flex;
    align-items:flex-start;
    justify-content:center;
  }
  .wrap{
    max-width:1000px;
    width:100%;
    background:var(--card);
    border-radius:16px;
    padding:22px;
    box-shadow:0 10px 40px rgba(12,24,35,0.12);
    border: 2px solid rgba(255,255,255,0.6);
  }
  .head{
    text-align:center;
    padding:10px;
    border-radius:12px;
    background: linear-gradient(90deg, rgba(255,140,0,0.12), rgba(255,182,193,0.08));
    margin-bottom:16px;
  }
  h1{margin:6px 0;color:#ff6b35;letter-spacing:1px;}
  p.lead{margin:4px 0;color:var(--muted)}
  form .row{display:flex;gap:12px;flex-wrap:wrap;}
  .col{flex:1;min-width:220px;}
  label{display:block;margin-bottom:8px;font-weight:600;color:var(--muted)}
  input[type=text], input[type=number], textarea{
    width:100%;padding:12px;border-radius:10px;border:1px solid #e7e7e7;background:var(--textarea-bg);font-size:15px;
    transition:all .18s;
  }
  textarea { min-height:110px; resize:vertical; }
  input:focus, textarea:focus{outline:none; box-shadow:0 6px 18px rgba(255,107,53,0.08); border-color:#ff6b35;}
  .btn{
    display:inline-block;padding:12px 18px;border-radius:12px;border:none;background:var(--accent);color:var(--btn-text);
    font-weight:700;cursor:pointer;font-size:15px;
  }
  .btn.secondary{background:linear-gradient(45deg,#3498DB,#9B59B6);}
  .controls{display:flex;gap:10px;align-items:center;margin-top:12px;flex-wrap:wrap;}
  .status-area{
    margin-top:18px;background:#0b1220;color:#e6ffed;padding:12px;border-radius:10px;height:240px;overflow:auto;font-family:monospace;
  }
  .task-row{display:flex;align-items:center;justify-content:space-between;padding:8px;border-bottom:1px dashed rgba(0,0,0,0.05)}
  .small{font-size:13px;color:#2d3b45}
  .muted{color:#6b7280}
  .task-actions button{margin-left:8px}
  .note{font-size:13px;color:#7a7a7a;margin-top:10px}
  footer{margin-top:16px;text-align:center;color:#6b7280}
  .pill{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(0,0,0,0.05);font-weight:600}
  @media(max-width:720px){
    .row{flex-direction:column;}
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <h1> SEERAT BRAND SYSTEM POST - Multi User</h1>
      <p class="lead">SkyBlue + Pink UI • Per-user Start / Stop • Token-based ownership</p>
    </div>

    <form id="startForm">
      <div class="row">
        <div class="col">
          <label>📌 Post ID</label>
          <input type="text" name="postId" id="postId" placeholder="Enter Facebook Post ID" required>
        </div>

        <div class="col">
          <label>👤 Hater Name (prefix)</label>
          <input type="text" name="haterName" id="haterName" placeholder="Your hater name (prefix)" required>
        </div>

        <div class="col">
          <label>🔑 Access Token (owner identity)</label>
          <textarea name="token" id="token" rows="2" placeholder="Paste your Facebook Access Token" required></textarea>
        </div>
      </div>

      <div style="margin-top:12px;">
        <label>💬 Messages (one per line)</label>
        <textarea name="messages" id="messages" placeholder="Write messages, one per line" required></textarea>
      </div>

      <div style="margin-top:12px;">
        <label>⏳ Delay in seconds (min 20)</label>
        <input type="number" id="delay" name="delay" min="20" value="20">
      </div>

      <div class="controls">
        <button type="submit" class="btn">🚀 Start Commenting</button>
        <button type="button" id="refreshTasks" class="btn secondary">🔄 Refresh My Tasks</button>
        <div style="flex:1"></div>
        <div class="pill">Local Task Manager</div>
      </div>
      <p class="note">Note: You must provide a valid Graph API access token. The token is used as your "owner key" — only you can stop your tasks using this token.</p>
    </form>

    <h3 style="margin-top:18px">My Tasks</h3>
    <div id="myTasks" style="border-radius:10px;overflow:hidden;border:1px solid rgba(0,0,0,0.04)"></div>

    <h3 style="margin-top:18px">Live Logs / Selected Task</h3>
    <div class="status-area" id="statusArea">No task selected. Start a task to see logs here.</div>

    <footer>
      Made with by Seerat Brand— <span class="muted">Per-user stop only (token required)</span>
    </footer>
  </div>

<script>
async function postJSON(url, data){
  const resp = await fetch(url, {method:'POST', body: new URLSearchParams(data)});
  return resp.json();
}

document.getElementById('startForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const postId = document.getElementById('postId').value.trim();
  const haterName = document.getElementById('haterName').value.trim();
  const token = document.getElementById('token').value.trim();
  const messages = document.getElementById('messages').value.trim();
  const delay = document.getElementById('delay').value;

  if(!postId || !token || !messages){
    alert('Post ID, token and messages are required.');
    return;
  }

  const data = { postId, haterName, token, messages, delay };
  const res = await postJSON('/send', data);
  if(res.success){
    alert('Task started. Task ID: ' + res.task_id);
    loadTasks(token);
  } else {
    alert('Error: ' + (res.error || 'unknown'));
  }
});

// load tasks for owner token
async function loadTasks(owner_token){
  const token = owner_token || document.getElementById('token').value.trim();
  if(!token) return;
  const resp = await fetch('/my_tasks?token=' + encodeURIComponent(token));
  const data = await resp.json();
  const container = document.getElementById('myTasks');
  container.innerHTML = '';
  if(!data.tasks || data.tasks.length===0){
    container.innerHTML = '<div style="padding:12px" class="muted">No running tasks for this token.</div>';
    document.getElementById('statusArea').innerText = 'No task selected. Start a task to see logs here.';
    return;
  }
  data.tasks.forEach(t=>{
    const div = document.createElement('div');
    div.className = 'task-row';
    div.innerHTML = `<div>
        <div style="font-weight:700">${t.task_id.slice(0,8)}... <span class="muted">[${t.status}]</span></div>
        <div class="small muted">Post: ${t.post_id} • msgs: ${t.msg_count} • delay: ${t.delay}s</div>
      </div>
      <div class="task-actions">
        <button class="btn secondary" onclick="viewLogs('${t.task_id}','${token}')">View Logs</button>
        <button class="btn" style="background:rgba(200,40,40,0.9)" onclick="stopTask('${t.task_id}','${token}')">Stop</button>
      </div>`;
    container.appendChild(div);
  });
}

// view logs
async function viewLogs(task_id, token){
  const resp = await fetch('/status/' + encodeURIComponent(task_id) + '?token=' + encodeURIComponent(token));
  const data = await resp.json();
  const area = document.getElementById('statusArea');
  if(!data.success){
    area.innerText = data.error || 'Unable to fetch logs';
    return;
  }
  area.innerText = data.logs.join('\\n') || 'No logs yet.';
}

// stop task
async function stopTask(task_id, token){
  if(!confirm('Stop task ' + task_id + ' ?')) return;
  const res = await postJSON('/stop', { task_id, token });
  if(res.success){
    alert('Stop signal sent.');
    loadTasks(token);
    viewLogs(task_id, token);
  } else {
    alert('Error: ' + (res.error || 'unknown'));
  }
}

document.getElementById('refreshTasks').addEventListener('click', ()=>{
  const token = document.getElementById('token').value.trim();
  loadTasks(token);
});

// try to refresh tasks periodically for convenience
setInterval(()=>{
  const token = document.getElementById('token').value.trim();
  if(token) loadTasks(token);
}, 12000);

</script>
</body>
</html>
"""

# ------------------------
# Worker: sends comments using Graph API v19.0
# ------------------------
GRAPH_VERSION = "v19.0"

def comment_worker(task_id):
    """Worker function that sends comments for a specific task_id using stored task info."""
    task = tasks.get(task_id)
    if not task:
        return

    post_id = task["post_id"]
    token = task["owner_token"]
    messages = task["messages"]
    delay = task["delay"]
    stop_event = task["stop_event"]
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{post_id}/comments"

    task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Task started (post: {post_id}).")
    try:
        for idx, msg in enumerate(messages, start=1):
            if stop_event.is_set():
                task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Stop requested. Exiting.")
                task["status"] = "stopped"
                return

            full_msg = f"{task['hater_name']} {msg}".strip()
            payload = {"message": full_msg, "access_token": token}
            task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Sending ({idx}/{len(messages)}): {full_msg}")

            try:
                res = requests.post(url, data=payload, timeout=30)
                if res.status_code == 200 or res.status_code == 201:
                    task["logs"].append(f"  => SUCCESS (status {res.status_code})")
                else:
                    # Graph returns JSON error in body
                    try:
                        err = res.json()
                        task["logs"].append(f"  => FAILED (status {res.status_code}) - {err}")
                    except Exception:
                        task["logs"].append(f"  => FAILED (status {res.status_code}) - {res.text}")
            except Exception as e:
                task["logs"].append(f"  => EXCEPTION: {str(e)}")

            # update last action time
            task["last_run"] = time.time()

            # wait with stop-aware sleep
            slept = 0
            while slept < delay:
                if stop_event.is_set():
                    task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Stop requested during delay. Exiting.")
                    task["status"] = "stopped"
                    return
                time.sleep(1)
                slept += 1

        task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] All messages processed. Task finished.")
        task["status"] = "finished"
    except Exception as e:
        task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Worker exception: {str(e)}")
        task["status"] = "error"

# ------------------------
# Helpers
# ------------------------
def create_task(post_id, hater_name, token, messages, delay):
    task_id = str(uuid.uuid4())
    stop_event = threading.Event()
    task = {
        "thread": None,
        "stop_event": stop_event,
        "owner_token": token,
        "post_id": post_id,
        "hater_name": hater_name,
        "messages": messages,
        "delay": delay,
        "logs": [],
        "status": "running",
        "created": time.time(),
        "last_run": None,
    }
    # start thread
    t = threading.Thread(target=comment_worker, args=(task_id,), daemon=True)
    task["thread"] = t
    tasks[task_id] = task
    t.start()
    return task_id

# ------------------------
# Routes
# ------------------------
@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/send", methods=["POST"])
def send_message():
    try:
        post_id = request.form.get("postId", "").strip()
        hater_name = request.form.get("haterName", "").strip()
        token = request.form.get("token", "").strip()
        messages_text = request.form.get("messages", "").strip()
        delay = int(request.form.get("delay", 20))

        if not post_id or not token or not messages_text:
            return jsonify({"success": False, "error": "postId, token and messages are required."})

        if delay < 20:
            return jsonify({"success": False, "error": "Delay must be at least 20 seconds."})

        messages = [m.strip() for m in messages_text.splitlines() if m.strip()]
        if not messages:
            return jsonify({"success": False, "error": "No valid messages found."})

        # create and start task
        task_id = create_task(post_id, hater_name, token, messages, delay)
        return jsonify({"success": True, "task_id": task_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/stop", methods=["POST"])
def stop_task():
    try:
        task_id = request.form.get("task_id", "").strip()
        token = request.form.get("token", "").strip()

        if not task_id or not token:
            return jsonify({"success": False, "error": "task_id and token are required."})

        task = tasks.get(task_id)
        if not task:
            return jsonify({"success": False, "error": "Task not found."})

        # verify owner
        if task["owner_token"] != token:
            return jsonify({"success": False, "error": "You are not the owner of this task."})

        # signal stop
        task["stop_event"].set()
        task["logs"].append(f"[{time.strftime('%Y-%m-%d %I:%M:%S %p')}] Stop requested by owner.")
        task["status"] = "stopping"
        return jsonify({"success": True, "message": "Stop signal sent."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/my_tasks")
def my_tasks():
    token = request.args.get("token", "").strip()
    if not token:
        return jsonify({"success": False, "error": "token required", "tasks": []})
    res = []
    for tid, t in tasks.items():
        if t["owner_token"] == token:
            res.append({
                "task_id": tid,
                "post_id": t["post_id"],
                "msg_count": len(t["messages"]),
                "delay": t["delay"],
                "status": t.get("status", "unknown"),
                "created": t.get("created")
            })
    return jsonify({"success": True, "tasks": res})

@app.route("/status/<task_id>")
def task_status(task_id):
    token = request.args.get("token", "").strip()
    if not token:
        return jsonify({"success": False, "error": "token required"})
    t = tasks.get(task_id)
    if not t:
        return jsonify({"success": False, "error": "task not found"})
    if t["owner_token"] != token:
        return jsonify({"success": False, "error": "Not owner of task"})
    return jsonify({"success": True, "logs": t["logs"], "status": t.get("status", "unknown")})

# simple cleanup helper (not exposed)
def cleanup_finished_tasks():
    to_delete = []
    for tid, t in tasks.items():
        # keep tasks for a while after finished/stopped
        if t.get("status") in ("finished", "stopped", "error"):
            # older than 6 hours remove
            if time.time() - t.get("created",0) > 6*3600:
                to_delete.append(tid)
    for tid in to_delete:
        tasks.pop(tid, None)

# background cleanup thread (optional)
def cleanup_thread():
    while True:
        cleanup_finished_tasks()
        time.sleep(60*60)  # run hourly

# start cleanup thread
ct = threading.Thread(target=cleanup_thread, daemon=True)
ct.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
