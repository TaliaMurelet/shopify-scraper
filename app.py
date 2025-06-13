from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Try to get PDP description text
            pdp_text = ""
            try:
                # Try common PDP selectors
                pdp_text = page.locator('.product__description, .product-single__description, .product-description, .rte').first.text_content()
            except:
                pdp_text = ""

            # Grab reviews
            reviews = []
            content = page.content().lower()

            if 'yotpo' in content:
                reviews = page.locator('.yotpo-review').all_text_contents()
            elif 'judgeme' in content:
                reviews = page.locator('.jdgm-review').all_text_contents()

            browser.close()

            return jsonify({
                "url": url,
                "pdp_text": pdp_text.strip() if pdp_text else "",
                "reviews_text": "\n".join(reviews) if reviews else ""
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



