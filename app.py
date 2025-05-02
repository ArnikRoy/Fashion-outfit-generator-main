from flask import Flask,url_for,redirect,request,render_template,Response;
from google import genai
import os
import PIL
from PIL import Image
import requests
import io
import sqlite3
import smtplib
import random
from dotenv import load_dotenv

load_dotenv()
import base64
from openai import OpenAI

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

client = genai.Client(api_key=os.getenv("GEM_API_KEY"))

files={"none": ''}
app = Flask(__name__)

def save_database(image,text_data):
    def convert_image_into_binary(filename):
        with open(filename, 'rb') as file:
            photo_image = file.read()
        return photo_image

    def insert_image(image):
        image_database = sqlite3.connect("./database/Image_data.db")
        data = image_database.cursor()
        insert_photo = convert_image_into_binary(image)
        data.execute("INSERT INTO Image (Image, text_feature) VALUES (:image, :text)", {'image': insert_photo, 'text': text_data})

        image_database.commit()
        image_database.close()

    def create_database():
        image_database = sqlite3.connect("./database/Image_data.db")
        data = image_database.cursor()
        data.execute("CREATE TABLE IF NOT EXISTS Image(Image BLOB)")
        image_database.commit()
        image_database.close()
    try:
        create_database()
        insert_image(image)
    except Exception as e:
        return str(e)
def generate_image(prop):
    def generate(user_input, index):
        def uniquify(path):
            filename, extension = os.path.splitext(path)
            counter = 1
            while os.path.exists(path):
                path = filename + " (" + str(counter) + ")" + extension
                counter += 1
            return path

        def query(payload):
            print(f"Sending request with payload: {payload}")

            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=payload["inputs"],
                config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
                )
            )
                
            # return response.content
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    imageByte = (part.inline_data.data)
                    # image.save('gemini-native-image.png')
                    # image.show()

            return imageByte
        try:
            # Add a random seed or timestamp to avoid caching
            payload = {
                "inputs": user_input,
                "seed": random.randint(1, 999999)  # Add randomness
            }
            image_bytes = query(payload)
            image = PIL.Image.open(io.BytesIO(image_bytes))
            image_path = "image" + str(index) + ".jpg"
            image.save("./static/images/" + image_path)
            print(f"Image saved as {image_path}")
            save_database("./static/images/" + image_path, prop)
        except Exception as e:
            print(f"Error generating image: {e}")
            return str(e)
    
    for i in range(1,9):
        generate(str(prop) + " outfit " + str(i), i)

@app.route('/')
def index():
    return render_template('opening.html')
@app.route('/read_more', methods=['GET', 'POST'])
def read_more_func():
    return render_template('index.html')

@app.route('/form_register', methods=['POST', 'GET'])
def fetch():
    try:
        req = request.form['search_bttn']
        print(req)
        generate_image(req)
        return render_template('index.html')
    except Exception as e:
        return str(e)
@app.route('/form_send',methods=['POST','GET'])
def Send():
    send_user=request.form['send_name']
    send_gmail=request.form['send_email']
    send_mess=request.form['send_mess']
    print(send_user,send_gmail,send_mess)
    send = "project.feedback.02@gmail.com"
    rec = "project.feedback.02@gmail.com"
    pas = "cmio eaap ofes wlwi"
    message = f"Subject: {send_gmail}\n\nMR/MRS {send_user} messaged you: {send_mess}"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(send, pas)
    server.sendmail(send, rec, message)
    return render_template('feedback.html')
@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    return render_template('feedback.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)





