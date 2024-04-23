from flask import Flask, render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import os
import shutil

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024     

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filename, operation):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)
    if img is None:
        flash('Error: Unable to process the image.')
        return None

    if operation == "cgray":
        img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        new_filename = f"{filename.rsplit('.', 1)[0]}_gray.jpg"
    elif operation == "cwebp":
        new_filename = f"{filename.rsplit('.', 1)[0]}.webp"
    else:
        flash('Error: Unsupported operation.')
        return None

    new_filepath = os.path.join('static', new_filename)
    cv2.imwrite(new_filepath, img_processed if operation == "cgray" else img)
    return new_filename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/edit", methods=["POST"])
def edit():
    operation = request.form.get("operation")
    if operation not in {"cgray", "cwebp"}:
        flash('Error: Unsupported operation.')
        return render_template("index.html")

    if 'file' not in request.files:
        flash('Error: No file part.')
        return render_template("index.html")

    file = request.files['file']
    if file.filename == '':
        flash('Error: No selected file.')
        return render_template("index.html")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_filename = process_image(filename, operation)
        if new_filename:
            flash(f"Image processed successfully. <a href='/download/{new_filename}' target='_blank'>Download processed image</a>")

    return render_template("index.html")

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)

if __name__ == "__main__":
    if os.path.exists('static'):
        shutil.rmtree('static') 
    os.makedirs('static')
    app.run(debug=True, port=5001)
