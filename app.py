from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing 'url' in request"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # Example: grab page title
            title = page.title()

            # Example: try to grab reviews if Yotpo or Judge.me present
            reviews = []
            if 'yotpo' in page.content().lower():
                reviews = page.locator('.yotpo-review').all_text_contents()
            elif 'judgeme' in page.content().lower():
                reviews = page.locator('.jdgm-review').all_text_contents()

            browser.close()

            return jsonify({
                "url": url,
                "title": title,
                "reviews": reviews
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

