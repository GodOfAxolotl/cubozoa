from flask import Flask, render_template, request, send_file
import tempfile
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex', delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(uploaded_file.read().decode('utf-8'))
        temp_file.seek(0)

        # LaTeX to PDF conversion
        try:
            subprocess.run(['pdflatex', '-output-directory=./static', '-jobname=output', '-interaction=nonstopmode', '-halt-on-error', temp_filename], check=True)
        except subprocess.CalledProcessError as e:
            # Fehlermeldung anzeigen
            error_message = f"Fehler beim Ausführen von pdflatex: {e}"
            return render_template('index.html', error_message=error_message)

    pdf_filename = './static/output.pdf'

    os.rename('./static/output.pdf', pdf_filename)
    os.unlink(temp_filename)

    return send_file(pdf_filename, as_attachment=True)



@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    latex_code = request.form['latexCode']

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex', delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(latex_code)
        temp_file.seek(0)

        # LaTeX to PDF conversion
        try:
            subprocess.run(['pdflatex', '-output-directory=./static', '-jobname=output', '-interaction=nonstopmode', '-halt-on-error', temp_filename], check=True)
        except subprocess.CalledProcessError as e:
            # Fehlermeldung anzeigen
            error_message = f"Fehler beim Ausführen von pdflatex: {e}"
            return render_template('index.html', error_message=error_message)

    pdf_filename = './static/output.pdf'

    os.rename('./static/output.pdf', pdf_filename)
    os.unlink(temp_filename)

    return send_file(pdf_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)