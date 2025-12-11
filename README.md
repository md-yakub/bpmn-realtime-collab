# 1. Backend (FastAPI/Websocket) Setup

## Location:

    /server

## Install dependencies:

    cd server
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## Run the backend:

    uvicorn main:app --reload --port 8000

## Backend tests:

    pytest -q

# 2. Frontend (React + Vite) Setup

## Location:

    /client

## Install dependencies:

    cd client
    npm install

## Run the frontend:

    npm run dev

## Open the app:

    Local:   http://localhost:5173

## run lint and prettier to improve the code:

    npm run lint
    nom run format
