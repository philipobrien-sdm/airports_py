import csv
from dataclasses import dataclass, field
from io import StringIO
from typing import List, Optional, Dict, Any
import urllib.parse
import sys


# ==========================================
# 1. EXPANDED DATA MODELS ("Structs")
# ==========================================

@dataclass
class RunwayDetails:
    designation: str
    length_ft: Optional[int]
    width_ft: Optional[int]
    surface: str
    lighted: bool


@dataclass
class Airport:
    # Identifiers & Class
    icao: str
    iata: Optional[str]
    local_code: Optional[str]
    name: str
    type: str
    scheduled_service: bool

    # Geography
    latitude: float
    longitude: float
    elevation_ft: float
    municipality: str
    region: str
    country: str

    # Infrastructure & Links
    runways: List[RunwayDetails] = field(default_factory=list)
    home_link: Optional[str] = None
    wikipedia_link: Optional[str] = None

    @property
    def google_maps_url(self) -> str:
        """Generates a clean Google Maps link using coordinates."""
        query = f"{self.latitude},{self.longitude}({self.name})"
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


# ==========================================
# 2. CLIENT IMPLEMENTATION
# ==========================================

class AirportLookup:
    def __init__(self):
        self.airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
        self.runways_url = "https://davidmegginson.github.io/ourairports-data/runways.csv"
        self._airport_cache: Dict[str, Dict[str, Any]] = {}
        self._runway_cache: Dict[str, List[RunwayDetails]] = {}
        self._initialized = False

    def initialize_data(self):
        """Fetches both datasets and indexes them completely into memory."""
        if self._initialized:
            return

        import requests

        print("Connecting to OurAirports global database...", flush=True)
        try:
            # 1. Fetch and parse airports with comprehensive metadata
            print("→ Downloading comprehensive airport registry...", flush=True)
            response = requests.get(self.airports_url)
            response.raise_for_status()
            f = StringIO(response.text)
            reader = csv.DictReader(f)

            for row in reader:
                icao = row['ident'].upper()
                if icao:
                    self._airport_cache[icao] = {
                        'name': row.get('name', 'Unknown'),
                        'iata': row.get('iata_code') if row.get('iata_code') else "N/A",
                        'local_code': row.get('local_code') if row.get('local_code') else "N/A",
                        'type': row.get('type', 'Unknown').replace('_', ' ').title(),
                        'scheduled_service': row.get('scheduled_service') == 'yes',
                        'lat': float(row['latitude_deg']) if row.get('latitude_deg') else 0.0,
                        'lon': float(row['longitude_deg']) if row.get('longitude_deg') else 0.0,
                        'elevation': float(row['elevation_ft']) if row.get('elevation_ft') else 0.0,
                        'municipality': row.get('municipality', 'Unknown'),
                        'region': row.get('iso_region', 'Unknown'),
                        'country': row.get('iso_country', 'Unknown'),
                        'home_link': row.get('home_link') if row.get('home_link') else None,
                        'wikipedia_link': row.get('wikipedia_link') if row.get('wikipedia_link') else None,
                    }

            # 2. Fetch and parse runways with precise layout variables
            print("→ Downloading structural runway datasets...", flush=True)
            response = requests.get(self.runways_url)
            response.raise_for_status()
            f = StringIO(response.text)
            reader = csv.DictReader(f)

            for row in reader:
                icao = row['airport_ident'].upper()
                le = row.get('le_ident', '')
                he = row.get('he_ident', '')
                designation = f"{le}/{he}" if le and he else (le or he)

                if icao and designation:
                    length = int(row['length_ft']) if row.get('length_ft') else None
                    width = int(row['width_ft']) if row.get('width_ft') else None
                    surface = row.get('surface', 'Unknown').strip().title()
                    lighted = row.get('lighted') == '1'

                    rw_detail = RunwayDetails(
                        designation=designation,
                        length_ft=length,
                        width_ft=width,
                        surface=surface if surface else "Unknown",
                        lighted=lighted
                    )

                    if icao not in self._runway_cache:
                        self._runway_cache[icao] = []

                    # Prevent duplicates if dataset repeats headings
                    if rw_detail not in self._runway_cache[icao]:
                        self._runway_cache[icao].append(rw_detail)

            self._initialized = True
            print("✓ Live database compiled successfully!\n" + "=" * 55 + "\n")

        except requests.exceptions.RequestException as e:
            print(f"\n[Error] Failed to stream data layers: {e}")
            sys.exit(1)

    def get_airport(self, icao_code: str) -> Optional[Airport]:
        """Looks up a structured airport profile."""
        self.initialize_data()

        icao = icao_code.upper().strip()
        if icao not in self._airport_cache:
            return None

        data = self._airport_cache[icao]
        runways = self._runway_cache.get(icao, [])

        return Airport(
            icao=icao,
            iata=data['iata'],
            local_code=data['local_code'],
            name=data['name'],
            type=data['type'],
            scheduled_service=data['scheduled_service'],
            latitude=data['lat'],
            longitude=data['lon'],
            elevation_ft=data['elevation'],
            municipality=data['municipality'],
            region=data['region'],
            country=data['country'],
            runways=runways,
            home_link=data['home_link'],
            wikipedia_link=data['wikipedia_link']
        )


# ==========================================
# 3. HIGH-FIDELITY TERMINAL INTERFACE
# ==========================================

def main():
    try:
        import requests
    except ImportError:
        print("[Error] Missing library setup. Run: pip install requests")
        sys.exit(1)

    client = AirportLookup()
    client.initialize_data()

    while True:
        try:
            icao_input = input("Enter ICAO code (or 'exit'): ").strip()
            if not icao_input:
                continue
            if icao_input.lower() == 'exit':
                print("Goodbye!")
                break

            airport = client.get_airport(icao_input)

            if airport:
                print("\n" + "═" * 55)
                print(f" ✈️  {airport.name}")
                print("═" * 55)
                print(f"  [IDENTIFIERS]  ICAO: {airport.icao}  |  IATA: {airport.iata}  |  Local: {airport.local_code}")
                print(
                    f"  [FACILITY]     Type: {airport.type}  |  Commercial Ops: {'Yes' if airport.scheduled_service else 'No'}")
                print(
                    f"  [LOCATION]     City: {airport.municipality}  |  Region: {airport.region}  |  Country: {airport.country}")
                print(f"  [GEOMETRICS]   Lat/Lon: {airport.latitude}, {airport.longitude}")
                print(f"                 Elevation: {int(airport.elevation_ft)} ft")

                print(f"\n  [RUNWAYS]:")
                if airport.runways:
                    for rw in airport.runways:
                        dim = f"{rw.length_ft}x{rw.width_ft} ft" if (rw.length_ft and rw.width_ft) else "Unknown Size"
                        lit = "⚠️ Night Ops Lit" if rw.lighted else "Unlit"
                        print(f"   • Strip {rw.designation:<7} |  Dim: {dim:<14} | Mat: {rw.surface:<12} | {lit}")
                else:
                    print("   • No active runway footprints found.")

                print(f"\n  [DIGITAL FEEDS]")
                print(f"   • Google Maps : {airport.google_maps_url}")
                if airport.home_link:
                    print(f"   • Web Portal  : {airport.home_link}")
                if airport.wikipedia_link:
                    print(f"   • Wikipedia   : {airport.wikipedia_link}")
                print("═" * 55 + "\n")
            else:
                print(f"❌ Airfield code '{icao_input.upper()}' could not be resolved.\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()