from flask import Flask, render_template, request, send_file, redirect, url_for
import tempfile
import subprocess
import os
import time
import uuid
import shutil
from werkzeug.utils import secure_filename

ALLOWED_TEXT_EXTENSIONS = {'txt', 'tex'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
UPLOAD_FOLDER = 'temp'


def create_app():
    app = Flask(__name__)

    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_TEXT_EXTENSIONS'] = ALLOWED_TEXT_EXTENSIONS
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ALLOWED_IMAGE_EXTENSIONS

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TEXT_EXTENSIONS

    def allowed_image(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

    def allowed_file_size(file):
        return file.content_length <= MAX_CONTENT_LENGTH

    def is_valid_content(content):
        # TODO, check if file is potentially harmful
        return True 

    def clean_temp_folder():
        current_time = time.time()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
                os.remove(file_path)


    @app.route('/')
    def index():
        clean_temp_folder() #TODO Not keep this as is omg
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template("login.html")

    @app.route('/registration')
    def registration():
        return render_template("registration.html")

    @app.route('/guide')
    def guide():
        return render_template("guide.html")

    @app.route('/tools')
    def tools():
        return render_template("tools.html")


    @app.route('/upload_file', methods=['POST'])
    def upload_file():
        uploaded_file = request.files['file']

        if 'file' not in request.files or uploaded_file.filename == '':
            return redirect(url_for('index'))

        if not allowed_file(uploaded_file.filename) or not allowed_file_size(uploaded_file):
            return redirect(url_for('index'))

        filename = secure_filename(uploaded_file.filename)
        
        file_content = uploaded_file.read().decode('utf-8')
        
        if not is_valid_content(file_content):
            return redirect(url_for('index'))

        return render_template('index.html', file_content=file_content)

    @app.route('/generate_pdf', methods=['POST'])
    def generate_pdf():
        latex_code = request.form['latexCode']

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex', delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(latex_code)
            temp_file.seek(0)

            # LaTeX to PDF conversion
            try:
                subprocess.run(['pdflatex', '-output-directory=./static/out', '-jobname=output', '-interaction=nonstopmode', '-halt-on-error', temp_filename], check=True)
            except subprocess.CalledProcessError as e:
                # Falsche Syntax
                error_message = f"An error has occured while executing pdflatex: {e} \n Please review your file syntax"
                return render_template('index.html', error_message=error_message)

        pdf_filename = './static/out/output.pdf'

        os.rename('./static/out/output.pdf', pdf_filename)
        os.unlink(temp_filename)

        return send_file(pdf_filename, as_attachment=True)


    @app.route('/save_as_txt', methods=['POST'])
    def save_as_txt():
        latex_code = request.form['latexCode']

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex', delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(latex_code)
            temp_file.seek(0)

            destination_directory = os.path.join(app.root_path, 'static', 'out')
            os.makedirs(destination_directory, exist_ok=True)

            destination = os.path.join(destination_directory, 'output.txt')

            shutil.copy(temp_filename, destination)

        os.unlink(temp_filename)

        return send_file(destination, as_attachment=True, download_name='output.txt')

    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        if 'file' not in request.files or request.files['file'].filename == '':
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_image(file.filename):
            filename = file.filename #str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower() TODO find solution for secure image upload
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return render_template('index.html', image_path=file_path)

        return redirect(request.url)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)