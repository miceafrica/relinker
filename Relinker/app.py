from flask import Flask, request, render_template, send_file
import os
import zipfile
import re
import shutil

app = Flask(__name__, template_folder='.')
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

# Ensure upload and processed directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_file():
    # Get the uploaded file and rename value
    zip_file = request.files.get('zip_file')
    rename_value = request.form.get('rename_value')

    if not zip_file or not rename_value:
        return "Missing zip file or rename value!", 400

    # Save the uploaded zip file
    zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
    zip_file.save(zip_path)

    # Extract the zip file
    extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    # Ensure "images" folder and "index.html" exist
    images_folder = os.path.join(extract_path, "images")
    html_path = os.path.join(extract_path, "index.html")

    if not os.path.exists(images_folder):
        return "No 'images' folder found in the zip file!", 400
    if not os.path.exists(html_path):
        return "No 'index.html' file found in the zip file!", 400

    # Rename images in the "images" folder
    renamed_files = rename_images(images_folder, rename_value)

    # Update the HTML file with renamed image URLs
    update_html(html_path, renamed_files)

    # Save the processed HTML file to the "processed" folder
    processed_html = os.path.join(PROCESSED_FOLDER, "index.html")
    shutil.copy(html_path, processed_html)

    # Return the results page with links to renamed images
    return render_template('results.html', renamed_files=renamed_files, html_file="index.html")


def rename_images(folder_path, rename_value):
    renamed_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                old_path = os.path.join(root, file)
                filename, ext = os.path.splitext(file)
                new_filename = f"{filename}_{rename_value}{ext}"
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                renamed_files.append((file, new_filename))
    return renamed_files


def update_html(html_path, renamed_files):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    for old_name, new_name in renamed_files:
        html_content = re.sub(rf'\b{old_name}\b', new_name, html_content)

    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found!", 404
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
