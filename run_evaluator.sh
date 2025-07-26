#!/bin/bash

echo "Team Ideas Evaluator"
echo "====================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Checking for required packages..."
echo

# Install required packages if not already installed
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Error installing required packages."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "All required packages installed successfully."
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found."
    echo "Creating .env file from template..."
    cp .env.template .env
    echo
    echo "Please edit the .env file to add your API keys."
    echo "Press Enter to continue without API keys (mock mode)..."
    read
fi

echo
echo "Running idea evaluator..."
echo

# Run the script
python3 Team_ideas_rating/idea_evaluator.py

echo
echo "Script execution completed."
echo
echo "Check the Team_ideas_rating folder for the output files:"
echo "- detailed_ratings.xlsx"
echo "- summary_ratings.xlsx"
echo

read -p "Press Enter to exit..."