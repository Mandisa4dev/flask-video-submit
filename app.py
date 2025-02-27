from flask import Flask, render_template, request, jsonify
import threading
import os

try:
    from automation_script import submit_video
except ModuleNotFoundError:
    def submit_video(video_url):
        print(f"Mock submission for: {video_url}")
        
app = Flask(__name__)

# Ensure templates folder exists
if not os.path.exists("templates"):
    os.makedirs("templates")
    with open("templates/index.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Video Submit</title>
</head>
<body>
    <h1>Submit Your Video</h1>
    <form id=\"videoForm\">
        <input type=\"text\" id=\"videoUrl\" placeholder=\"Enter video URL\" required>
        <button type=\"submit\">Submit</button>
    </form>
    <p id=\"response\"></p>
    <script>
        document.getElementById("videoForm").addEventListener("submit", function(event) {
            event.preventDefault();
            const url = document.getElementById("videoUrl").value;
            fetch("/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_url: url })
            })
            .then(response => response.json())
            .then(data => document.getElementById("response").innerText = data.message)
            .catch(error => console.error("Error:", error));
        });
    </script>
</body>
</html>""")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({"error": "No video URL provided"}), 400
    
    video_url = data['video_url']
    thread = threading.Thread(target=submit_video, args=(video_url,))
    thread.daemon = True  # Ensures the thread exits when the main program does
    thread.start()
    
    return jsonify({"message": "Submission started", "video_url": video_url})

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
