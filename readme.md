# 🌍 Airports.py - ICAO Airport & Runway Lookup Tool

`airports.py` is a lightweight, zero-configuration Python CLI application that transforms any 4-letter ICAO airport code into detailed geographic, structural, and navigation data. 

Powered by real-time updates from the open-source **OurAirports** dataset, it instantly fetches crucial information, handles runway mappings, and generates precise, click-to-open Google Maps URLs for any matching airfield globally.

---

## ✨ Features

- **🚀 Instant Lookups:** $O(1)$ memory-cached data structure allows fast lookups without multiple API requests.
- **🏗️ Object-Oriented Design:** Returns structured `Airport` and `Runway` datatypes (Python Data Classes).
- **🛤️ Runway Configurations:** Resolves low-end and high-end runway headings (e.g., `09/27`, `18R/36L`).
- **📍 Dynamic Mapping:** Generates optimized Google Maps URLs pinned directly to the airport's exact coordinates.
- **🌐 Global Coverage:** Looks up international hubs, regional fields, and heliports alike.

---

## 🛠️ Requirements & Installation

The script is entirely self-contained and only requires Python 3.7+ and the `requests` library.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
   
2. Install dependency:
   pip install requests

   3. Usage:

          python airports.py

         Connecting to OurAirports data source...
         → Downloading airport directory...
         → Downloading runway configurations...
         ✓ Data loaded successfully!
         ========================================

          Enter an ICAO code (e.g., EGLL, KJFK, YSSY) or 'exit' to quit: KLAX

          Searching for 'KLAX'...

          ----------------------------------------
          ICAO CODE     : KLAX 
          NAME          : Los Angeles International Airport
   
          LATITUDE      : 33.942501
          LONGITUDE     : -118.407997
          ELEVATION     : 128 ft
          RUNWAYS       : 06L/24R, 06R/24L, 07L/25R, 07R/25L
          MAPS LINK     : [https://www.google.com/maps/search/?api=1&query=33.942501,-118.407997(Los%20Angeles%20International%20Airport)](https://www.google.com/maps/search/?api=1&query=33.942501,-118.407997(Los%20Angeles%20International%20Airport))
         ----------------------------------------

