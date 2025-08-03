from flask import Flask, request, jsonify, render_template_string
import os
import threading

app = Flask(__name__)

# Thread-safe global state dictionary with lock
pending_message = {
    "indu_message": "",
    "yaswanth_reply": "",
    "approved": False
}
message_lock = threading.Lock()

# HTML template for the review page
review_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Review Page</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f4f8;
            color: #333;
            padding: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: #ffffff;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
        }
        h1 {
            font-size: 28px;
            margin-bottom: 20px;
            text-align: center;
            color: #2c3e50;
        }
        .message-box {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
        }
        .indu-text {
            margin-top: 5px;
            font-size: 16px;
            line-height: 1.5;
        }
        .form label {
            font-weight: bold;
            display: block;
            margin-bottom: 8px;
            color: #34495e;
        }
        .form textarea {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ccc;
            font-size: 16px;
            resize: vertical;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .form button {
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .form button:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Review Pending Message</h1>
        <div class="message-box">
            <p><strong>Indu Message:</strong></p>
            <p class="indu-text">{{ indu_message }}</p>
        </div>
        <form method="POST" action="/approve" class="form">
            <label for="yaswanth_reply">Yaswanth Reply:</label>
            <textarea id="yaswanth_reply" name="yaswanth_reply" rows="6">{{ yaswanth_reply }}</textarea>
            <button type="submit">✅ Approve</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/generate', methods=['POST'])
def generate_update_message():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON data"}), 400

    indu_message = data.get("indu_message")
    yaswanth_reply = data.get("yaswanth_reply")

    if not indu_message or not yaswanth_reply:
        return jsonify({"status": "error", "message": "Both indu_message and yaswanth_reply required"}), 400

    # Update global pending message with thread safety
    with message_lock:
        pending_message["indu_message"] = indu_message
        pending_message["yaswanth_reply"] = yaswanth_reply
        pending_message["approved"] = False

    # Respond with reply so the client gets the message immediately
    return jsonify({
        "status": "success",
        "message": "Message received for review",
        "yaswanth_reply": yaswanth_reply
    }), 200

@app.route('/', methods=['GET'])
def review_page():
    # Render the review page with the current pending_message
    with message_lock:
        indu_msg = pending_message["indu_message"]
        yaswanth_reply = pending_message["yaswanth_reply"]
    return render_template_string(review_page_template, 
                                  indu_message=indu_msg, 
                                  yaswanth_reply=yaswanth_reply)

@app.route('/', methods=['POST'])
def root_update_message():
    # Accept JSON data and update the global pending_message
    data = request.get_json()
    if data and "indu_message" in data and "yaswanth_reply" in data:
        with message_lock:
            pending_message["indu_message"] = data["indu_message"]
            pending_message["yaswanth_reply"] = data["yaswanth_reply"]
            pending_message["approved"] = False
        return jsonify({"status": "success", "message": "Message updated successfully"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/approve', methods=['POST'])
def approve_message():
    # Accept the edited yaswanth_reply and mark the message as approved
    edited_reply = request.form.get("yaswanth_reply")
    if edited_reply is not None:
        with message_lock:
            pending_message["yaswanth_reply"] = edited_reply
            pending_message["approved"] = True
        return jsonify({"status": "success", "message": "Message approved successfully"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/status', methods=['GET'])
def status():
    # Return the current status of the pending_message
    with message_lock:
        approved = pending_message["approved"]
        yaswanth_reply = pending_message["yaswanth_reply"]
    return jsonify({
        "approved": approved,
        "yaswanth_reply": yaswanth_reply
    }), 200

if __name__ == '__main__':
    # Use environment variable to control debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
