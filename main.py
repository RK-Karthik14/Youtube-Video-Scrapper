from flask import Flask, request, jsonify
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from tqdm import tqdm
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

def scrape_and_send(email, channel_name):
    try:
        # Scraping Process
        link = f'https://www.youtube.com/@{channel_name}/videos'
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
        chrome_options.add_argument("--window-size=1920x1080")
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(link)
        time.sleep(10)

        # Scroll to load videos
        code = "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
        last_height = browser.execute_script(code)

        while True:
            browser.find_element(by=By.TAG_NAME, value="body").send_keys(Keys.END)
            time.sleep(7)
            new_height = browser.execute_script(code)
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        contents = soup.find('ytd-rich-grid-renderer')

        data = []

        for sp in contents.find_all('ytd-rich-item-renderer'):
            title = sp.find('a', class_='yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media').get('title')
            video_link = 'https://www.youtube.com' + sp.find('a', class_='yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media').get('href')
            views = sp.find('span', class_='inline-metadata-item style-scope ytd-video-meta-block').text
            time_ago = sp.find_all('span', class_='inline-metadata-item style-scope ytd-video-meta-block')[1].text
            try:
                duration = sp.find('div', class_='badge-shape-wiz__text').text
            except:
                duration = np.nan
            try:
                image_src = sp.find('img', class_='yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded').get('src').split('?')[0]
            except:
                image_src = np.nan
            data.append([title, time_ago, duration, np.nan ,views, np.nan, image_src, video_link])
            
        for i in tqdm(range(len(data))):
            video_link = data[i][7]
            
            browser.get(video_link)
            time.sleep(5)
            
            vb_soup = BeautifulSoup(browser.page_source, 'html.parser')
            likes_btn = vb_soup.find('like-button-view-model')
            likes = likes_btn.find('div', class_='yt-spec-button-shape-next__button-text-content').text
            description = ''
            for vb_sp in vb_soup.find_all('yt-attributed-string', class_='style-scope ytd-text-inline-expander'):
                description += vb_sp.text

            data[i][3] = likes
            data[i][5] = description

        # Save data to a CSV file
        filename = f"{channel_name}_videos.csv"
        df = pd.DataFrame(data, columns=['title', 'time_ago', 'duration', 'likes', 'views', 'description', 'thumbnail_src', 'video_src'])
        df.to_csv(filename, index=False)

        # Send Email
        sender_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        subject = "YouTube Channel Data CSV"
        body = f"Please find the attached CSV file containing the video data for the channel: {channel_name}"

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        message.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)  # Clean up file

@app.route('/scrape-and-send', methods=['POST'])
def handle_request():
    data = request.json
    email = data.get('email')
    channel_name = data.get('channel_name')

    if not email or not channel_name:
        return jsonify({'error': 'Email and channel name are required'}), 400

    # Start the scraping and email process in a new thread
    threading.Thread(target=scrape_and_send, args=(email, channel_name)).start()

    # Immediate response
    return jsonify({'message': 'Status will be sent to your mail in due time'}), 202

if __name__ == '__main__':
    app.run(debug=True)
