
from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def scrape_shopify_product(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # Attempt to extract product title
        title = await page.title()

        # Try common Shopify PDP selectors
        description = await page.locator(".product__description, .product-description, [itemprop='description']").first.text_content()
        description = description.strip() if description else "No description found"

        # Close browser
        await browser.close()

        return {
            "url": url,
            "title": title,
            "description": description
        }

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    try:
        result = asyncio.run(scrape_shopify_product(url))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
