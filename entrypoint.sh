#!/bin/bash
set -e

echo "🚀 Starting Meal Planner..."

# Run database setup (initialization + migration)
echo "📊 Setting up database..."
python db_setup.py

# Start the application
echo "🍽️ Starting Flask application..."
exec python app.py