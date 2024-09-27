import requests
from enum import Enum

def get_round_trip_fares(departure_airport, arrival_airport, adult_pax_count,
                         outbound_date_from, outbound_date_to,
                         inbound_date_from, inbound_date_to, duration_from, duration_to):
    url = "https://www.ryanair.com/api/farfnd/v4/roundTripFares"
    
    params = {
        "departureAirportIataCode": departure_airport,
        "adultPaxCount": adult_pax_count,
        "outboundDepartureDateFrom": outbound_date_from,
        "outboundDepartureDateTo": outbound_date_to,
        "inboundDepartureDateFrom": inbound_date_from,
        "inboundDepartureDateTo": inbound_date_to,
        "durationFrom": duration_from,
        "durationTo": duration_to
    }

    if arrival_airport != "":
        params["arrivalAirportIataCode"] = arrival_airport
    
    # Make the request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the response in JSON format
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

class Fare:
    def __init__(self, departure_iata, departure_airport, arrival_iata, arrival_airport, price, outbound_date, inbound_date, trip_length):
        self.departure_iata = departure_iata
        self.departure_airport = departure_airport
        self.arrival_iata = arrival_iata
        self.arrival_airport = arrival_airport
        self.price = price
        self.outbound_date = outbound_date
        self.inbound_date = inbound_date
        self.trip_length = trip_length

    def __str__(self):
        return f"{self.departure_airport} ({self.departure_iata}) <<-->> {self.arrival_airport} ({self.arrival_iata}) on {self.outbound_date} and back on {self.inbound_date} ({self.trip_length} days) for {self.price} EUR"

    def __repr__(self):
        return str(self)

class SortBy(Enum):
    NONE = ""
    PRICE = "price"
    TRIP_LENGTH = "trip_length"

def sort_results(results, sort_by: SortBy):
    if sort_by == SortBy.NONE:
        return results
    return sorted(results, key=lambda result: getattr(result, sort_by.value))

# Airport codes:
#   TSF: Treviso Airport
#   VCE: Marco polo Airport
#   ZAG: Zagreb Airport
#   VIE: Vienna Airport
if __name__ == "__main__":

    # ----------------------------------------------
    # Settings for the search
    # ----------------------------------------------
    departure_airports = ["TSF", "VCE", "ZAG"]
    arrival_airports = [""]
    passenger_count = 1
    outbound_date_from = "2024-09-30"
    outbound_date_to = "2024-10-08"
    inbound_date_from = "2024-10-12"
    inbound_date_to = "2024-10-19"
    duration_from = 7
    duration_to = 10
    max_roundtrip_price = 100
    sort_by = SortBy.PRICE
    # ----------------------------------------------

    results = []

    if len(departure_airports) == 0:
        print("No departure airports specified.")
        exit()
    
    if len(arrival_airports) == 0:
        arrival_airports = [""]
    
    print("Finding the cheapest round-trip flights...")   

    for departure_airport in departure_airports:
        for arrival_airport in arrival_airports:
            result = get_round_trip_fares(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                adult_pax_count=passenger_count,
                outbound_date_from=outbound_date_from,
                outbound_date_to=outbound_date_to,
                inbound_date_from=inbound_date_from,
                inbound_date_to=inbound_date_to,
                duration_from=duration_from,
                duration_to=duration_to
            )

            for res in result["fares"]:
                price = res["summary"]["price"]["value"]

                if price > max_roundtrip_price:
                    continue

                # Get airport names
                dep_iata = res["outbound"]["departureAirport"]["iataCode"]
                dep_airport = res["outbound"]["departureAirport"]["name"]
                ret_iata = res["inbound"]["departureAirport"]["iataCode"]
                ret_airport = res["inbound"]["departureAirport"]["name"]

                # Get other information
                dep_date = res["outbound"]["departureDate"]
                ret_date = res["inbound"]["departureDate"]
                trip_length = res["summary"]["tripDurationDays"]

                results.append(Fare(
                    dep_iata, dep_airport, 
                    ret_iata, ret_airport, 
                    price, dep_date, ret_date, trip_length))

    # Display results
    sorted_results = sort_results(results, sort_by)
    for res in sorted_results:
        print(res)

    print(f"Search completed. Found {len(results)} results.")