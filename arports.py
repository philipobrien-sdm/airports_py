import csv
from dataclasses import dataclass
from io import StringIO
from typing import List, Optional, Dict, Any
import urllib.parse
import sys


# ==========================================
# 1. DATA MODELS (The "Structs")
# ==========================================

@dataclass
class Airport:
    icao: str
    name: str
    latitude: float
    longitude: float
    elevation_ft: float
    runways: List[str]

    @property
    def google_maps_url(self) -> str:
        """Generates a direct Google Maps link using coordinates."""
        # Using a clean search query string format: 'lat,lon(Airport Name)'
        query = f"{self.latitude},{self.longitude}({self.name})"
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


# ==========================================
# 2. CLIENT IMPLEMENTATION
# ==========================================

class AirportLookup:
    def __init__(self):
        # Using highly reliable, open-source daily updates from OurAirports
        self.airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
        self.runways_url = "https://davidmegginson.github.io/ourairports-data/runways.csv"
        self._airport_cache: Dict[str, Dict[str, Any]] = {}
        self._runway_cache: Dict[str, list] = {}
        self._initialized = False

    def initialize_data(self):
        """Fetches datasets and indexes them in memory for O(1) lookups."""
        if self._initialized:
            return

        import requests  # Imported here so the script only errors if missing upon execution

        print("Connecting to OurAirports data source...", flush=True)
        try:
            # 1. Fetch and parse airports
            print("→ Downloading airport directory...", flush=True)
            response = requests.get(self.airports_url)
            response.raise_for_status()
            f = StringIO(response.text)
            reader = csv.DictReader(f)

            for row in reader:
                icao = row['ident'].upper()
                if icao:
                    self._airport_cache[icao] = {
                        'name': row['name'],
                        'lat': float(row['latitude_deg']) if row['latitude_deg'] else 0.0,
                        'lon': float(row['longitude_deg']) if row['longitude_deg'] else 0.0,
                        'elevation': float(row['elevation_ft']) if row['elevation_ft'] else 0.0,
                    }

            # 2. Fetch and parse runways
            print("→ Downloading runway configurations...", flush=True)
            response = requests.get(self.runways_url)
            response.raise_for_status()
            f = StringIO(response.text)
            reader = csv.DictReader(f)

            for row in reader:
                icao = row['airport_ident'].upper()
                le = row['le_ident']
                he = row['he_ident']
                designation = f"{le}/{he}" if le and he else (le or he)

                if icao and designation:
                    if icao not in self._runway_cache:
                        self._runway_cache[icao] = []
                    # Keep track of unique runway alignments
                    if designation not in self._runway_cache[icao]:
                        self._runway_cache[icao].append(designation)

            self._initialized = True
            print("✓ Data loaded successfully!\n" + "=" * 40 + "\n")

        except requests.exceptions.RequestException as e:
            print(f"\n[Error] Failed to fetch data from remote servers: {e}")
            sys.exit(1)

    def get_airport(self, icao_code: str) -> Optional[Airport]:
        """Looks up airport data by code."""
        self.initialize_data()

        icao = icao_code.upper().strip()
        if icao not in self._airport_cache:
            return None

        data = self._airport_cache[icao]
        runways = self._runway_cache.get(icao, [])

        return Airport(
            icao=icao,
            name=data['name'],
            latitude=data['lat'],
            longitude=data['lon'],
            elevation_ft=data['elevation'],
            runways=runways
        )


# ==========================================
# 3. INTERACTIVE CLI RUNNER
# ==========================================

def main():
    # Quick prerequisite check
    try:
        import requests
    except ImportError:
        print("[Error] This script requires the 'requests' library.")
        print("Please run: pip install requests")
        sys.exit(1)

    client = AirportLookup()

    # Pre-warm cache so the input prompt feels snappy
    client.initialize_data()

    while True:
        try:
            icao_input = input("Enter an ICAO code (e.g., EGLL, KJFK, YSSY) or 'exit' to quit: ").strip()
            if not icao_input:
                continue
            if icao_input.lower() == 'exit':
                print("Goodbye!")
                break

            print(f"\nSearching for '{icao_input.upper()}'...")
            airport = client.get_airport(icao_input)

            if airport:
                print("\n" + "-" * 40)
                print(f"  ICAO CODE     : {airport.icao}")
                print(f"  NAME          : {airport.name}")
                print(f"  LATITUDE      : {airport.latitude}")
                print(f"  LONGITUDE     : {airport.longitude}")
                print(f"  ELEVATION     : {int(airport.elevation_ft)} ft")
                print(f"  RUNWAYS       : {', '.join(airport.runways) if airport.runways else 'None listed'}")
                print(f"  MAPS LINK     : {airport.google_maps_url}")
                print("-" * 40 + "\n")
            else:
                print(f"❌ No airport found with ICAO code '{icao_input.upper()}'. Try another code.\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()