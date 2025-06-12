from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Try to get PDP description (very basic selector, might need refining per site)
            try:
                description = page.query_selector("div[id*=description], .product-description, .rte").inner_text()
            except:
                description = "No description found."

            # Try Yotpo reviews
            reviews = []
            try:
                page.wait_for_selector(".yotpo-review", timeout=5000)
                review_elements = page.query_selector_all(".yotpo-review .content-review")
                for r in review_elements[:5]:
                    reviews.append(r.inner_text())
            except:
                reviews = ["No Yotpo reviews found."]

            browser.close()
            return jsonify({
                "description": description,
                "reviews": reviews
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
