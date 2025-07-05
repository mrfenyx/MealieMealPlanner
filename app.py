from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import requests
import config

app = Flask(__name__)

def get_meal_plan(start_date, end_date):
    headers = {"Authorization": f"Bearer {config.MEALIE_API_TOKEN}"}
    url = (
        f"{config.MEALIE_URL}/api/households/mealplans"
        f"?start_date={start_date}&end_date={end_date}"
    )
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
    except Exception:
        return {
            "error": "Invalid JSON response",
            "status_code": response.status_code,
            "response_text": response.text,
            "url": url
        }, response.status_code

    # Enrich each item with correct image URL using slug and fixed filename
    for item in data.get("items", []):
        recipe = item.get("recipe", {})
        id = recipe.get("id")
        slug = recipe.get("slug")
        if id:
            item["image_url"] = f"{config.MEALIE_URL}/api/media/recipes/{id}/images/min-original.webp"
        else:
            item["image_url"] = None
        if slug:
            item["recipe_url"] = f"{config.MEALIE_URL}/g/home/r/{slug}"
        else:
            item["recipe_url"] = None

    return data

@app.route("/")
def index():
    today = datetime.now().date()
    start = today - timedelta(days=7)
    end = today + timedelta(days=7)
    data = get_meal_plan(start.isoformat(), end.isoformat())
    return render_template("index.html", items=data.get("items", []))

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_meal(item_id):
    headers = {"Authorization": f"Bearer {config.MEALIE_API_TOKEN}"}
    url = f"{config.MEALIE_URL}/api/households/mealplans/{item_id}"

    response = requests.delete(url, headers=headers)
    
    if response.ok:  # Accept any 2xx, including 200 with JSON body
        return jsonify({"success": True})
    else:
        return jsonify({
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }), 400