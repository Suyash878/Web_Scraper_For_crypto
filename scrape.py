from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from bs4 import BeautifulSoup
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

currency_data = []
crypto_news = []

def scrape_currency():
    """
    Function to scrape news from BBC and update the global headlines and subtext lists.
    """
    global currency_data, crypto_news
    currency_data = []
    crypto_news = []
    try:
        # Fetch and parse the HTML
        html_text = requests.get('https://www.gadgets360.com/finance/crypto-currency-price-in-india-inr-compare-bitcoin-ether-dogecoin-ripple-litecoin').text
        soup = BeautifulSoup(html_text, 'lxml')

        # Extract the name of the currency and its short form
        names = soup.find_all('div', class_='_flx crynm')
        prices = soup.find_all('td', class_='_rft _cpr')
        percentage_changes = soup.find_all('span', class_='_chper')
        changes = soup.find_all('span', class_='symb')
        news = soup.find_all('li', class_='_flx')

        for name, price, percentage_change, change in zip(names, prices, percentage_changes, changes):
            currency_data.append({
                'name': name.text.strip(),
                'price': price.text.strip(),
                'change': change.text.strip(),
                'percentage_change': percentage_change.text.strip()
            })

        for new in news:
            news_text = new.text.strip()
            if news_text:  # Only append non-empty text
                crypto_news.append({
                    'news': news_text
                })
    except Exception as e:
        print(f"Error occurred during scraping: {e}")

@app.route('/crypto', methods=['GET'])
def get_crypto_data():
    """
    API endpoint to fetch the latest scraped news and other reads.
    """
    return jsonify(currency_data, crypto_news)

if __name__ == '__main__':
    # Scheduler setup
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_currency, 'interval', minutes=10)  # Run every 10 minutes
    scheduler.start()

    # Run the first scrape immediately
    scrape_currency()

    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=10000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
