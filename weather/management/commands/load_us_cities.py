"""
Management command to load 100 largest US cities by population.
Run with: python manage.py load_us_cities
"""
from django.core.management.base import BaseCommand
from weather.models import Location


US_CITIES = [
    ("New York", 40.7128, -74.0060, "NY", "New York"),
    ("Los Angeles", 34.0522, -118.2437, "CA", "California"),
    ("Chicago", 41.8781, -87.6298, "IL", "Illinois"),
    ("Houston", 29.7604, -95.3698, "TX", "Texas"),
    ("Phoenix", 33.4484, -112.0742, "AZ", "Arizona"),
    ("Philadelphia", 39.9526, -75.1652, "PA", "Pennsylvania"),
    ("San Antonio", 29.4241, -98.4936, "TX", "Texas"),
    ("San Diego", 32.7157, -117.1611, "CA", "California"),
    ("Dallas", 32.7767, -96.7970, "TX", "Texas"),
    ("San Jose", 37.3382, -121.8863, "CA", "California"),
    ("Austin", 30.2672, -97.7431, "TX", "Texas"),
    ("Jacksonville", 30.3322, -81.6557, "FL", "Florida"),
    ("Fort Worth", 32.7555, -97.3308, "TX", "Texas"),
    ("Columbus", 39.9612, -82.9988, "OH", "Ohio"),
    ("Charlotte", 35.2271, -80.8431, "NC", "North Carolina"),
    ("San Francisco", 37.7749, -122.4194, "CA", "California"),
    ("Indianapolis", 39.7684, -86.1581, "IN", "Indiana"),
    ("Seattle", 47.6062, -122.3321, "WA", "Washington"),
    ("Denver", 39.7392, -104.9903, "CO", "Colorado"),
    ("Boston", 42.3601, -71.0589, "MA", "Massachusetts"),
    ("El Paso", 31.7619, -106.4850, "TX", "Texas"),
    ("Nashville", 36.1627, -86.7816, "TN", "Tennessee"),
    ("Detroit", 42.3314, -83.0458, "MI", "Michigan"),
    ("Oklahoma City", 35.4676, -97.5164, "OK", "Oklahoma"),
    ("Portland", 45.5152, -122.6784, "OR", "Oregon"),
    ("Las Vegas", 36.1699, -115.1398, "NV", "Nevada"),
    ("Memphis", 35.1495, -90.0490, "TN", "Tennessee"),
    ("Louisville", 38.2527, -85.7585, "KY", "Kentucky"),
    ("Baltimore", 39.2904, -76.6122, "MD", "Maryland"),
    ("Milwaukee", 43.0389, -87.9065, "WI", "Wisconsin"),
    ("Albuquerque", 35.0844, -106.6504, "NM", "New Mexico"),
    ("Tucson", 32.2226, -110.9747, "AZ", "Arizona"),
    ("Fresno", 36.7378, -119.7871, "CA", "California"),
    ("Mesa", 33.4153, -111.8310, "AZ", "Arizona"),
    ("Sacramento", 38.5816, -121.4944, "CA", "California"),
    ("Atlanta", 33.7490, -84.3880, "GA", "Georgia"),
    ("Kansas City", 39.0997, -94.5786, "MO", "Missouri"),
    ("Long Beach", 33.7701, -118.1937, "CA", "California"),
    ("Raleigh", 35.7796, -78.6382, "NC", "North Carolina"),
    ("New Orleans", 29.9511, -90.2623, "LA", "Louisiana"),
    ("Arlington", 38.8816, -77.1043, "VA", "Virginia"),
    ("Saint Paul", 44.9537, -93.0900, "MN", "Minnesota"),
    ("Minneapolis", 44.9778, -93.2650, "MN", "Minnesota"),
    ("Anaheim", 33.8353, -117.9145, "CA", "California"),
    ("Aurora", 39.7294, -104.8202, "CO", "Colorado"),
    ("Stockton", 37.9577, -121.2911, "CA", "California"),
    ("Riverside", 33.9806, -117.2757, "CA", "California"),
    ("Corpus Christi", 27.5793, -97.3964, "TX", "Texas"),
    ("Lexington", 38.0297, -84.4784, "KY", "Kentucky"),
    ("Henderson", 35.9757, -115.1763, "NV", "Nevada"),
    ("Plano", 33.0198, -96.6989, "TX", "Texas"),
    ("Anchorage", 61.2181, -149.9003, "AK", "Alaska"),
    ("Tampa", 27.9506, -82.4572, "FL", "Florida"),
    ("Irvine", 33.6846, -117.8265, "CA", "California"),
    ("Chula Vista", 32.6401, -117.0842, "CA", "California"),
    ("Aurora", 39.7294, -104.8202, "CO", "Colorado"),
    ("Santa Ana", 33.7455, -117.8677, "CA", "California"),
    ("St. Louis", 38.6270, -90.1994, "MO", "Missouri"),
    ("Laredo", 27.5064, -99.5075, "TX", "Texas"),
    ("Lubbock", 33.5779, -101.8552, "TX", "Texas"),
    ("Garland", 32.9127, -96.6385, "TX", "Texas"),
    ("Phoenix", 33.4484, -112.0742, "AZ", "Arizona"),
    ("Chandler", 33.3062, -111.8413, "AZ", "Arizona"),
    ("Pittsburgh", 40.4406, -79.9959, "PA", "Pennsylvania"),
    ("Irving", 32.8140, -96.9489, "TX", "Texas"),
    ("Norfolk", 36.8507, -76.2859, "VA", "Virginia"),
    ("Huntsville", 34.7304, -86.5861, "AL", "Alabama"),
    ("Orlando", 28.5421, -81.3723, "FL", "Florida"),
    ("Madison", 43.0731, -89.4012, "WI", "Wisconsin"),
    ("Scottsdale", 33.4942, -111.9261, "AZ", "Arizona"),
    ("Greensboro", 36.0726, -79.7920, "NC", "North Carolina"),
    ("Spokane", 47.6587, -117.4260, "WA", "Washington"),
    ("Fontana", 34.0922, -117.4350, "CA", "California"),
    ("Winston-Salem", 36.0999, -80.2440, "NC", "North Carolina"),
    ("Durham", 35.9940, -78.8986, "NC", "North Carolina"),
    ("Miami", 25.7617, -80.1918, "FL", "Florida"),
    ("Modesto", 37.6688, -121.0193, "CA", "California"),
    ("Shreveport", 32.5149, -93.7373, "LA", "Louisiana"),
    ("Baton Rouge", 30.4515, -91.1871, "LA", "Louisiana"),
    ("Newark", 40.7357, -74.1724, "NJ", "New Jersey"),
    ("Hialeah", 25.8576, -80.3781, "FL", "Florida"),
    ("Laredo", 27.5064, -99.5075, "TX", "Texas"),
    ("Birmingham", 33.5186, -86.8104, "AL", "Alabama"),
    ("Boise", 43.6150, -116.2023, "ID", "Idaho"),
    ("Richmond", 37.5407, -77.4360, "VA", "Virginia"),
    ("Toledo", 41.6639, -83.5558, "OH", "Ohio"),
    ("Garland", 32.9127, -96.6385, "TX", "Texas"),
    ("Glendale", 33.6386, -112.1853, "AZ", "Arizona"),
    ("Fremont", 37.5485, -122.2710, "CA", "California"),
    ("Brownsville", 25.9017, -97.4975, "TX", "Texas"),
    ("North Las Vegas", 36.1989, -115.1175, "NV", "Nevada"),
    ("Baton Rouge", 30.4515, -91.1871, "LA", "Louisiana"),
    ("Irving", 32.8140, -96.9489, "TX", "Texas"),
    ("Jersey City", 40.7178, -74.0431, "NJ", "New Jersey"),
    ("Moreno Valley", 33.7534, -117.2312, "CA", "California"),
    ("Chula Vista", 32.6401, -117.0842, "CA", "California"),
    ("Yonkers", 40.9496, -73.8648, "NY", "New York"),
]


class Command(BaseCommand):
    help = "Load 100 largest US cities into Location model"

    def handle(self, *args, **options):
        count = 0
        skipped = 0

        for city_name, latitude, longitude, state_code, state_name in US_CITIES:
            # Create unique name: "City, State"
            full_name = f"{city_name}, {state_code}"

            # Check if location already exists
            if Location.objects.filter(name=full_name).exists():
                skipped += 1
                continue

            # Create location
            Location.objects.create(
                name=full_name,
                city=city_name,
                country="United States",
                latitude=latitude,
                longitude=longitude,
                timezone="US/Eastern",  # Can be refined per location
                is_active=True,
            )
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded {count} cities. "
                f"({skipped} already existed)"
            )
        )
