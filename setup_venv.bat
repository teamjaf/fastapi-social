@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo.
echo To activate the virtual environment, run:
echo venv\Scripts\activate.bat
echo.
echo To run the application with Gunicorn:
echo gunicorn app.main:app -c gunicorn.conf.py
echo.
echo Or to run with uvicorn for development:
echo uvicorn app.main:app --host 0.0.0.0 --port 9090 --reload
