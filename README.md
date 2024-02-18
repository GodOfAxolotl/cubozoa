This is very, very work in progress! DO NOT HOST THIS PUBLICLY AND DO NOT USE YOUR GOOD PASSWORDS FOR LOGIN!!!

# LaTeX Editor - Cubozoa

Cubozoa is a web application that allows users to edit, generate PDFs, and save LaTeX documents. This project is developed using Flask, Bootstrap, and other web technologies. It enables everyone to host latex without thinking about latex packages.

## Table of Contents

- [Features](#features)
- [Roadmap](#roadmap)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features

- Upload and edit LaTeX documents
- Selfhostable and free, for ever
- Generate PDFs from LaTeX code
- Save LaTeX code as a TXT file
- Embed uploaded images into LaTeX code

## Roadmap

1. **Image Upload and Embedding**
   - Allow users to upload images in better ways.
   - Implement image embedding in the LaTeX code.

2. **User Authentication**
   - Add user registration and login functionalities for saving on server side
   - Add a Database fir users and their files and images

3. **User Dashboard**
   - Create a personalized dashboard for users to manage their documents.
   - Also, create an Admin Dashboard to see what is happening 

4. **Collaborative Editing**
   - Enable collaborative editing of LaTeX documents.

5. **Improved UI/UX**
   - Enhance the user interface for a better user experience.
   - Add a Latex Guide

6. **Additional Tools**
    - Some additional tools like snippets or templates

## Installation (Linux)

1. Clone the repository:

   ```bash```
   ```git clone https://github.com/GodOfAxolotl/cubozoa.git```
   ```cd cubozoa```

2. Install dependencies
    ```pip install -r requirements.txt```

3. Setup virtual environment
    ```python -m venv venv```

   Activate the virtual environment:

    ```source venv/bin/activate```

4. Run the application with Gunicorn

    ```gunicorn -w 4 -b 0.0.0.0:5000 "__init__:create_app()"```

    -w 4 is the number of worker threads, -b is your ip and port, change as you like.

5. Optional: Start this as a service
    1. Add a user cube, do not give him root
    2. adjust the cubozoa.service file to your liking
    3. move it to /etc/systemd/system
    4. ```systemctl daemon-reload```
    5. ```systemctl enable cubozoa```
    6. ```systemctl start cubozoa```

6. Optional: Proxy with nginx
    I will not explain this because the software is not safe and should not be hosted other than on a machine or maybe a local network for now.

## Usage
    * Upload a LaTeX file or start a new one.
    * Edit the LaTeX code in the provided textarea.
    * Use the buttons to generate a PDF or save as TXT.
    * To embed an image, use the image upload feature.

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it for any purpose.