from flask import Flask , render_template , Response , request , url_for
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation , **kwargs):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cwebp": 
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg": 
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng": 
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "Denoising":
            imgProcessed = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "Sharpening":
            kernel = np.array([[0, -1, 0], 
                   [-1, 5,-1], 
                   [0, -1, 0]])
            imgProcessed =cv2.filter2D(img, -1, kernel)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "equalization":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgProcessed = cv2.equalizeHist(gray)
            res = np.hstack((gray, imgProcessed))
            newFilename += "_equalized.png"
            cv2.imwrite(newFilename, res)
            return newFilename
        case "rotate":
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            angle = 45
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            imgProcessed=cv2.warpAffine(img, M, (w, h))
            newFilename = f"static/{filename.rsplit('.', 1)[0]}_rotated.png"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "blur":
            imgProcessed = cv2.GaussianBlur(img, (15, 15), 0)
            newFilename = f"static/{filename}"
            return newFilename
        case "edge":
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgProcessed= cv2.Canny(gray_image, 100, 200)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "RGB":
            # gray_image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
            imgProcessed =cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
    pass

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")

    return render_template("index.html")
if __name__=='__main__':
    app.run(debug=True)