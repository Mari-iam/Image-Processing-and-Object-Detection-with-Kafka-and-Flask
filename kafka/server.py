import os
import uuid
import sys
import sqlite3
from producer import on_image_upload
from flask import Flask, redirect, render_template_string, request, send_from_directory, jsonify

IMAGES_DIR = "images"
MAIN_DB = "main.db"

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(MAIN_DB)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure the images directory exists
if not os.path.exists(IMAGES_DIR):
    os.mkdir(IMAGES_DIR)

# Initialize the database
con = get_db_connection()
con.execute("CREATE TABLE IF NOT EXISTS image (id TEXT PRIMARY KEY, filename TEXT, object TEXT)")
con.close()

@app.route('/', methods=['GET'])
def index():
    con = get_db_connection()
    cur = con.cursor()
    res = cur.execute("SELECT * FROM image")
    images = res.fetchall()
    con.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-auto-rows: minmax(100px, auto);
  gap: 20px;
}
img {
   display: block;
   max-width:100%;
   max-height:100%;
   margin-left: auto;
   margin-right: auto;
}
.img {
   height: 270px;
}
.label {
   height: 30px;
  text-align: center;
}
</style>
</head>
<body>
<form method="post" enctype="multipart/form-data">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="file" accept="image/x-png,image/gif,image/jpeg" />
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>
<div class="container">
{% for image in images %}
<div>
<div class="img"><img src="/images/{{ image.filename }}"></div>
<div class="label">{{ image.object | default('undefined', true) }}</div>
</div>
{% endfor %}
</div>

<script>
  var ws = new WebSocket("ws://localhost:8765");  // Update port if necessary
  ws.onmessage = function(event) {
    var message = JSON.parse(event.data);
    if (message.error) {
      alert("Error: " + message.error);
    } else if (message.completed) {
      alert("Task completed: " + message.completed);
    }
    // Refresh page or update content based on message
    window.location.reload();
  };
  ws.onerror = function(event) {
    console.error("WebSocket error: ", event);
    // Handle WebSocket errors if necessary
  };
</script>
</body>
</html>
    """, images=images)

@app.route('/images/<path:path>', methods=['GET'])
def image(path):
    return send_from_directory(IMAGES_DIR, path)

@app.route('/object/<id>', methods=['PUT'])
def set_object(id):
    con = get_db_connection()
    cur = con.cursor()
    json_data = request.json
    obj = json_data['object']
    cur.execute("UPDATE image SET object = ? WHERE id = ?", (obj, id))
    con.commit()
    con.close()
    return '{"status": "OK"}'

@app.route('/', methods=['POST'])
def upload_file():
    f = request.files['file']
    ext = f.filename.split('.')[-1]
    id = uuid.uuid4().hex
    filename = f"{id}.{ext}"
    f.save(os.path.join(IMAGES_DIR, filename))

    con = get_db_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO image (id, filename, object) VALUES (?, ?, ?)", (id, filename, ""))
    con.commit()
    con.close()

    on_image_upload(id, filename)  # Send image metadata to Kafka

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=(int(sys.argv[1]) if len(sys.argv) > 1 else 5000))
