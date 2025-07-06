from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import config
from db import (
    init_db, mark_done, re_add, get_all_done_ids,
    get_shopping_ids, add_shopping_items
)

app = Flask(__name__)
CORS(app)
init_db()

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

    for item in data.get("items", []):
        recipe = item.get("recipe", {})
        _id = recipe.get("id")
        slug = recipe.get("slug")
        if _id:
            item["image_url"] = (
                f"{config.MEALIE_URL}/api/media/recipes/{_id}/images/min-original.webp"
            )
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
    done_ids = set(get_all_done_ids())
    visible_items = [
        item for item in data.get("items", [])
        if item.get("id") not in done_ids
    ]
    return render_template(
        "index.html",
        items=visible_items,
        current_page="index"
    )


@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_meal(item_id):
    headers = {"Authorization": f"Bearer {config.MEALIE_API_TOKEN}"}
    url = f"{config.MEALIE_URL}/api/households/mealplans/{item_id}"
    response = requests.delete(url, headers=headers)
    if response.ok:
        return jsonify({"success": True})
    else:
        return jsonify({
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }), 400


@app.route("/done/<int:item_id>", methods=["POST"])
def mark_meal_done(item_id):
    mark_done(item_id)
    return jsonify({"success": True})


@app.route("/readd/<int:item_id>", methods=["POST"])
def readd_meal(item_id):
    re_add(item_id)
    return jsonify({"success": True})


@app.route("/done")
def view_done():
    today = datetime.now().date()
    start = today - timedelta(days=30)
    end = today + timedelta(days=7)
    data = get_meal_plan(start.isoformat(), end.isoformat())
    done_ids = set(get_all_done_ids())
    done_items = [
        item for item in data.get("items", [])
        if item.get("id") in done_ids
    ]
    return render_template(
        "done.html",
        items=done_items,
        current_page="done"
    )


@app.route("/shopping-list")
def shopping_list():
    # 1. Pull the same 2-week window
    today = datetime.now().date()
    start = today - timedelta(days=7)
    end = today + timedelta(days=7)
    data = get_meal_plan(start.isoformat(), end.isoformat())

    # 2. Exclude any "done" items
    done_ids = set(get_all_done_ids())
    upcoming = [
        item for item in data.get("items", [])
        if item.get("id") not in done_ids
    ]

    # 3. For each slug, fetch full recipe & grab its ingredient list
    headers = {"Authorization": f"Bearer {config.MEALIE_API_TOKEN}"}
    recipes = []
    for item in upcoming:
        slug = item["recipe"]["slug"]
        resp = requests.get(
            f"{config.MEALIE_URL}/api/recipes/{slug}", headers=headers
        )
        if not resp.ok:
            continue
        recipe = resp.json()
        ingredients = [
            {"id": ing.get("referenceId"), "display": ing.get("display")}
            for ing in recipe.get("recipeIngredient", [])
        ]
        recipes.append({
            "name": recipe.get("name"),
            "ingredients": ingredients
        })

    shopping_ids = get_shopping_ids()

    return render_template(
        "shopping_list.html",
        recipes=recipes,
        shopping_ids=shopping_ids,
        current_page="shopping_list"
    )


@app.route("/shopping-list/add", methods=["POST"])
def add_to_shopping_list():
    data = request.get_json() or {}
    items = data.get("ingredients", [])
    db_items = [(itm["id"], itm["name"]) for itm in items]
    add_shopping_items(db_items)
    return jsonify({"success": True})


@app.route("/add/<slug>", methods=["POST"])
def add_to_plan(slug):
    headers = {
        "Authorization": f"Bearer {config.MEALIE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    recipe_resp = requests.get(
        f"{config.MEALIE_URL}/api/recipes/{slug}", headers=headers
    )
    if not recipe_resp.ok:
        return jsonify(
            success=False,
            message=f"Could not fetch recipe “{slug}”: {recipe_resp.text}"
        ), recipe_resp.status_code

    recipe = recipe_resp.json()
    recipe_id = recipe.get("id")
    if not recipe_id:
        return jsonify(success=False, message="Missing recipe ID"), 500

    target_date = (datetime.now().date() + timedelta(days=7)).isoformat()
    payload = {
        "date":       target_date,
        "recipeId":   recipe_id,
        "entryType":  "dinner"
    }
    add_resp = requests.post(
        f"{config.MEALIE_URL}/api/households/mealplans",
        headers=headers, json=payload
    )
    if add_resp.ok:
        return jsonify(success=True), 201
    else:
        return jsonify(success=False, message=add_resp.text), add_resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
