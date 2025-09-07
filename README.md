# Mealie Meal Planner to OurGroceries

This is a simple web application that connects to your Mealie instance, fetches your meal plan, and generates a shopping list that can be synced with the OurGroceries app.

## Features

*   Fetches and displays your meal plan from Mealie.
*   Allows you to mark meals as "done".
*   Generates a shopping list based on your upcoming meals.
*   Syncs your shopping list with OurGroceries.
*   Provides a simple web interface to manage your meal plan and shopping list.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd MealieMealPlanner
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the root of the project and add the following environment variables:

    ```
    MEALIE_API_TOKEN=<your-mealie-api-token>
    MEALIE_API_URL=<your-mealie-api-url>
    MEALIE_URL=<your-mealie-url>
    OG_USERNAME=<your-ourgroceries-username>
    OG_PASSWORD=<your-ourgroceries-password>
    OG_LIST_NAME=<your-ourgroceries-list-name>
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

    The application will be available at `http://localhost:5000`.

## Docker

You can also run this application using Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t mealie-meal-planner .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 -v $(pwd)/.env:/.env mealie-meal-planner
    ```

    Alternatively, you can use the `docker-compose.yml` file:

    ```bash
    docker-compose up -d
    ```
