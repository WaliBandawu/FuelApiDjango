# 🚗 Fuel Route Optimization API

A Django-based REST API that intelligently calculates the most fuel-efficient and cost-effective driving routes across the United States. By leveraging real-time fuel price data and geolocation services, this API helps users identify optimal refueling stops along their journey.

---

## ✨ Features

- 🔍 **Optimized Fuel Stops**: Recommends the cheapest fuel stations along your route.
- 🗺️ **Geolocation Support**: Converts city/state names into geographic coordinates.
- 💰 **Cost-Aware Routing**: Calculates total fuel cost based on MPG and fuel prices.
- 📍 **Map View**: Visualizes the driving route and refueling points.

---

## ⚙️ Prerequisites

- Python 3.x
- Django
- Django REST Framework
- OpenRouteService API key (for routing)

---

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/WaliBandawu/FuelApiDjango.git
cd FuelApiDjango
```

2. **Install Pipenv (if not already installed):**
```bash
pip install pipenv
```

3. **Install dependencies via Pipenv:**
```bash
pipenv install
```

4. **Activate the virtual environment:**
```bash
pipenv shell
```

5. **Apply database migrations:**
```bash
python manage.py migrate
```

---

## 🚀 Usage

1. **Start the development server:**
```bash
python manage.py runserver
```

2. **Use the following endpoints:**

### 🔄 Optimize Route
```http
POST /api/optimize-route/
```
Send start and destination city/state to receive a list of optimal refueling stops along the route.

### 🗺️ Route Map View
```http
GET /route-map/
```
Returns a visual map of the calculated route and refuel locations.

---

## 🧪 Example Request (Optimize Route)

```json
POST /api/optimize-route/
{
  "start": "Los Angeles, CA",
  "destination": "Denver, CO"
}
```

---

## 🤝 Contributing

1. Fork this repository
2. Create a new branch: `git checkout -b feature/awesome-feature`
3. Commit your changes: `git commit -m "Add awesome feature"`
4. Push to your branch: `git push origin feature/awesome-feature`
5. Open a Pull Request

---

## 📄 License

[MIT License or your preferred license]

---

## 📬 Contact

For questions or suggestions, feel free to reach out:  
**Your Name** – [wabandawu@gmail.com]
