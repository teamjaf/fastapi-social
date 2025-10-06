#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "To run the application with Gunicorn:"
echo "gunicorn app.main:app -c gunicorn.conf.py"
echo ""
echo "Or to run with uvicorn for development:"
echo "uvicorn app.main:app --host 0.0.0.0 --port 9090 --reload"
