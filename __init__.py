from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from user_db import UserDB
from models import db, UploadedImages
import tempfile
import subprocess
import hashlib
import os
import time
import uuid
import shutil
from werkzeug.utils import secure_filename

ALLOWED_TEXT_EXTENSIONS = {'txt', 'tex'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpeg'}
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
UPLOAD_FOLDER = 'temp'


def create_app():
    app = Flask(__name__)

    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_TEXT_EXTENSIONS'] = ALLOWED_TEXT_EXTENSIONS
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ALLOWED_IMAGE_EXTENSIONS
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
    app.config['SECRET_KEY'] = '8322c780ba9951754043be8980121e113b400b07549949087b5404a36490bff9'

    login_manager = LoginManager(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    user_db = UserDB()


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
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        current_time = time.time()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
                os.remove(file_path)


    @app.route('/')
    def index():
        clean_temp_folder() #TODO Not keep this as is omg
        return render_template('index.html', user_db=user_db)


    @login_manager.user_loader
    def load_user(user_id):
        return user_db.get_user_by_id(int(user_id))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = user_db.get_user_by_username(username)

            if user:
                print(f"User found: {user.username}")
                if user_db.check_password(username, password):
                    print("Password is correct. Logging in.")
                    login_user(user)
                    return render_template('index.html')
                else:
                    print("Password is incorrect.")
                    return render_template('login.html', error_message='Password is not correct')
            else:
                print("User not found.")

            return render_template('login.html', error_message='Credentials not correct')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return render_template('index.html')

    @app.route('/registration', methods=['GET', 'POST'])
    def registration():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            existing_user = user_db.get_user_by_username(username)
            if existing_user:
                return render_template('registration.html', error_message='Username not available')

            new_user = user_db.add_user(username, email, password)
            login_user(new_user)
            return redirect(url_for('index'))

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
        if not current_user.is_authenticated:
            return render_template('login.html', error_message='Login required to upload images')

        uploaded_file = request.files['file']

        if 'file' not in request.files or uploaded_file.filename == '':
            return redirect(url_for('index'))

        username = current_user.username
        hashed_folder_name = current_user.userhash
        user_folder = os.path.join('./instance', hashed_folder_name)

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(user_folder, filename)
        if os.path.exists(file_path):
            return render_template('index.html', error_message='This image has already been uploaded')

        uploaded_file.save(file_path)

        current_user.image_folder = hashed_folder_name
        new_uploaded_image = UploadedImages(filename=filename, user=current_user)
        db.session.add(new_uploaded_image)
        db.session.commit()

        return render_template('index.html', image_path=file_path, error_message='')

    
    return app

if __name__ == '__main__':
    app = create_app()

    app.run(debug=True)