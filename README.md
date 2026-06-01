# 🕰️ ClockOut — "Wann kannst du heute gehen?"

A beautiful, smart personal time-tracking assistant that tells you exactly when you can finish your workday. Simply capture a screenshot of your company's hour-tracking dashboard, paste it into the clean web app, and **ClockOut** does the rest.

In addition to calculating your exact clock-out time, it automatically fetches the daily lunch menu from the local personal restaurant (Eurest Schindler) and plans your public transport connections home directly from the nearest station (Buchrain).

---

## 🌟 Key Features

*   **⚡ Clipboard OCR Integration**: No tedious manual logging. Simply take a screenshot of your clock-in/out timestamps and paste it (`Ctrl+V` / `Cmd+V`) directly into the browser.
*   **🧠 Intelligent Workday Math**:
    *   Extracts all clock-in and clock-out stamps using **EasyOCR**.
    *   Automatically calculates elapsed time and break durations.
    *   Enforces a minimum required lunch break (defaults to 30 minutes), or uses your actual break duration if you took a longer one.
    *   Calculates your exact remaining target hours (defaults to 8 hours).
*   **🍽️ Lunch Menu Scraper**: Fetches and parses the daily specials from the Schindler Eurest Personalrestaurant website using **BeautifulSoup4** so you know what's for lunch.
*   **🚆 Swiss Public Transport Planner**: Integrates with the open Swiss public transport API to fetch the next 6 train departures from **Buchrain** to your target destination (e.g., Luzern), timed precisely around your calculated clock-out time (supporting custom walking times and margins).

---

## 🛠️ Technology Stack

### Backend
*   **FastAPI**: A high-performance Python 3 web framework for the API endpoints.
*   **EasyOCR**: A robust neural network-based text recognition engine to parse times from images.
*   **Pillow (PIL)**: Image decoding and preprocessing.
*   **BeautifulSoup4**: HTML parsing for the restaurant menu web scraper.
*   **httpx**: Async HTTP requests for external Swiss transport API lookups.
*   **Pydantic**: Data validation and type enforcement.

### Frontend
*   **Vue 3 (Composition API)**: Modern, highly responsive frontend framework utilizing `<script setup>` with TypeScript.
*   **Vite**: Next-generation, blazing-fast frontend build tool and development server.
*   **Vanilla CSS**: Custom premium UI featuring soft glows, modern cards, and glassmorphic micro-animations.

---

## 📂 Project Directory Structure

```text
clockout/
├── python_backend/              # FastAPI Backend Services
│   ├── main.py                  # API endpoints, middleware, & server setup
│   ├── ocr.py                   # EasyOCR text extraction & time string regex parser
│   ├── func.py                  # Workday end-time calculations & ISO duration parsing
│   ├── get_menus.py             # Web scraper for Schindler Eurest restaurant
│   ├── API.md                   # Dedicated API documentation
│   └── requirements.txt         # Backend Python packages
│
├── vue-frontend-clockout/       # Vue 3 Frontend Web App
│   ├── src/
│   │   ├── App.vue              # Application shell
│   │   ├── main.ts              # App initialization
│   │   └── views/
│   │       └── clockoutView.vue # Dashboard with clipboard listener & API bindings
│   ├── package.json             # NPM dependencies & scripts
│   ├── vite.config.ts           # Vite configuration
│   └── tsconfig.json            # TypeScript configuration
│
├── reqeust.http                 # Sample HTTP REST requests with base64 testing payload
└── README.md                    # Core project documentation
```

---

## 🚀 Getting Started

### Prerequisites
*   **Python**: Version 3.10 or higher
*   **Node.js**: Version 18.0 or higher
*   **Package Managers**: `pip` (Python) and `npm` (Node)

---

### 1. Backend Setup

1.  Navigate into the backend directory:
    ```bash
    cd python_backend
    ```

2.  Create and activate a virtual environment (optional but recommended):
    ```bash
    # MacOS / Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Start the FastAPI development server:
    ```bash
    uvicorn python_backend.main:api --reload --port 8000
    ```
    The backend API will now be available at `http://localhost:8000`.

---

### 2. Frontend Setup

1.  Navigate into the frontend directory:
    ```bash
    cd vue-frontend-clockout
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Run the development server:
    ```bash
    npm run dev
    ```
    Open `http://localhost:5173` (or the URL outputted in your console) to view the web app!

---

## 🔌 API Documentation

All API routes are served by the FastAPI application in `python_backend/main.py`.

A full description of request schemas, path/query parameters, and response structures can be found in the dedicated documentation file:
👉 **[python_backend/API.md](file:///Users/oiven/dev/clockout/python_backend/API.md)**

---

## 💡 How It Works (Calculation Logic)

Under the hood, `python_backend/func.py` executes a precise workday calculation:
1.  **Parsing Timestamps**: The server receives a chronological list of timestamps from the OCR parser (e.g., `07:41` (In), `11:31` (Out), `12:14` (In)).
2.  **Break / Lunch Duration**:
    *   It measures the intervals between successive `Out` and `In` events:
        $$\text{Break} = \text{Clock-In (Afternoon)} - \text{Clock-Out (Morning)}$$
    *   In the example: `12:14 - 11:31 = 43 minutes`.
    *   If the calculated break is less than the minimum statutory break duration (30 minutes), a **30-minute** break is enforced. Otherwise, your actual break duration is subtracted from the day.
3.  **End Time Output**:
    *   Adds the required target workday duration (8 hours) and the calculated break time to the very first clock-in timestamp (`07:41`):
        $$\text{End Time} = \text{Start Time} + \text{Target Workday} + \text{Break}$$
        $$\text{End Time} = \text{07:41} + \text{8 hours} + \text{43 minutes} = \text{16:24}$$

---

## 🛡️ License

This project is open-source and licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.