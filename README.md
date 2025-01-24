# YouTube Channel Scraper and Emailer

This project is a Python Flask-based web application that allows users to scrape video data from any YouTube channel and receive the data as a CSV file via email. The app provides a simple API endpoint where users can submit their email and the YouTube channel id.

## Features
* Scrapes video data (title, views, duration, etc.) from a specified YouTube channel.
* Sends the scraped data as a CSV file to the user's email.
* Provides immediate feedback to the user about the status of the request.
* Shows the status of the information scrapping in the console
* Fully self-contained and deployable with no additional tools required.

## Technologies Used
* **Flask**: Backend framework for handling API requests.
* **Selenium**: Web scraping tool to interact with YouTube.
* **BeautifulSoup**: For parsing YouTube page HTML.
* **Pandas**: For processing and exporting data to CSV.
* **dotenv**: For managing environment variables securely.
* **SMTP**: For sending emails with attachments.
* **TQDM**: For showing the status of the information scrape

## Setup Instructions
### Prerequistes
1. Install Python (>= 3.7).
2. Install Google Chrome and download the compatible [ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads).
### Installation
1. Clone the repository
```
    git clone https://github.com/RK-Karthik14/Youtube-Video-Scrapper.git
```
2. Create virtual environment
```
    python -m venv venv
    venv\Scripts\activate #windows command
```
3. Install the required dependencies
```
    pip install -r requirements.txt
```

4. Create app password for your mail id [here](https://youtu.be/weA4yBSUMXs?feature=shared)
5. Create a ``` .env ``` file in the project root and add your email credentials
```
    EMAIL_ADDRESS=email@gmail.com
    EMAIL_PASSWORD=your_app_password
```
## How to Run Locally
1. Start the Flask Server
```
    python app.py
```
2. The app will be available at ```http://127.0.0.1:5000/```.
3. Test the API using tools like Postman.
    * Endpoint: ```POST /scrape-and-send```
    * Body (raw data json format)
    ```
        {
            "email": "example@domain.com",
            "channel_name": "FlutterCool"
        }

    ```
    * **Note**: Provide channel id
    ![IMG](/images/img1.png)
