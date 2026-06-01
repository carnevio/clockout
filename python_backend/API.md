# 🔌 ClockOut Backend API Documentation

All backend endpoints are built using **FastAPI** and served by the application in `python_backend/main.py`. The server runs locally on port `8000` by default.

---

## 🧭 Endpoint Index
*   [`POST /process-img`](#1-post-process-img) — Process an uploaded timecard image using OCR & calculate workday end time.
*   [`GET /menus`](#2-get-menus) — Retrieve daily lunch specials from Schindler's Eurest restaurant.
*   [`GET /transport/{target_location}`](#3-get-transporttarget_location) — Query Swiss public transport connections from Buchrain.

---

## 1. `POST /process-img`
This endpoint takes a base64 encoded screenshot of your timecard application, parses the clock-in/out timestamps via the **EasyOCR** engine, and returns the calculated workday completion time.

### Request
*   **Method**: `POST`
*   **Path**: `/process-img`
*   **Headers**: `Content-Type: application/json`
*   **Payload Schema** (Pydantic model `Item`):
    *   `data`: `string` (The raw image file encoded as a base64 string).

#### Example Request Body
```json
{
  "data": "iVBORw0KGgoAAAANSUhEUgAAAd4AAAD+CAYAAACURWRBAAAAAXNSR0IArs4c6QAAAARn..."
}
```

### Response
*   **Status Code**: `200 OK`
*   **Content Type**: `application/json`
*   **Response Body Schema**:
    *   `end_time`: `string` (ISO 8601 formatted datetime indicating when the user completes their target hours).
    *   `times`: `list[string]` (ISO 8601 formatted list of all timestamps extracted by the OCR parser).

#### Example Response Body
```json
{
  "end_time": "2026-06-01T17:11:00+02:00",
  "times": [
    "2026-06-01T07:41:00+02:00",
    "2026-06-01T11:31:00+02:00",
    "2026-06-01T12:14:00+02:00"
  ]
}
```

---

## 2. `GET /menus`
Scrapes and compiles the latest daily lunch menu and descriptions from the Schindler Eurest Personalrestaurant.

### Request
*   **Method**: `GET`
*   **Path**: `/menus`

### Response
*   **Status Code**: `200 OK`
*   **Content Type**: `application/json`
*   **Response Body Schema**:
    A JSON object where each key represents the menu ID/sorting rank (e.g., `1`, `2`) containing:
    *   `name`: `string` (The title of the menu item, e.g. Tagesschlager or Vegi).
    *   `desc`: `string` (Detailed description of the meal).

#### Example Response Body
```json
{
  "1": {
    "name": "Menü 1: Tagesschlager",
    "desc": "Zarte Kalbsbrust mit Kartoffelstock und Saisongemüse"
  },
  "2": {
    "name": "Menü 2: Vegi",
    "desc": "Rotes Linsencurry mit Basmatireis und Naan-Brot"
  }
}
```

---

## 3. `GET /transport/{target_location}`
Provides real-time connection suggestions departing from the **Buchrain** train station (the station nearest to Schindler) towards your custom destination, timed directly around your calculated clock-out time.

### Request
*   **Method**: `GET`
*   **Path**: `/transport/{target_location}`
*   **Path Parameters**:
    *   `target_location` (string): Destination city/station (e.g., `Luzern`, `Zürich`).
*   **Query Parameters**:
    *   `end_time` (datetime, required): The core timestamp used as a reference point for transport calculations (ISO format).
    *   `walking_time` (timedelta, optional): Walking time offset (in ISO 8601 duration format, e.g. `PT10M` for 10 mins). Defaults to `0`.
    *   `minus_time` (timedelta, optional): Margin of advance time allowed to catch a train before your official clock-out time. Defaults to `0`.

#### Example Request
```http
GET http://localhost:8000/transport/Luzern?end_time=2026-06-01T17:11:00&walking_time=PT10M
```

### Response
*   **Status Code**: `200 OK`
*   **Content Type**: `application/json`
*   **Response**: Prints upcoming departures and connections in the backend terminal console and pulls connection metadata from `transport.opendata.ch`.

---

## 🛠️ Testing the API
You can test the endpoints manually using the root-level [`reqeust.http`](../reqeust.http) file with an IDE REST Client extension, or access FastAPI's interactive Swagger UI documentation at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**
