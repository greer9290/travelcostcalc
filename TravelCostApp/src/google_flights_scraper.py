from selectolax.lexbor import LexborHTMLParser
import time

def get_google_flights_page(playwright, origin, destination, depart_date, return_date):
    print(f"Debug: get_google_flights_page called with parameters:")
    print(f"  origin: {origin}")
    print(f"  destination: {destination}")
    print(f"  departure_date: {depart_date}")
    print(f"  return_date: {return_date}")

    page = playwright.chromium.launch(headless=True).new_page()
    page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

    # type "From"
    origin_field = page.query_selector_all('.e5F5td')[0]
    origin_field.click()
    time.sleep(0.4)
    origin_field.type(origin)
    time.sleep(0.4)
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')

    # type "To"
    destination_field = page.query_selector_all('.e5F5td')[1]
    time.sleep(0.4)
    destination_field.type(destination)
    time.sleep(0.4)
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')

    # type "Departure date"
    departure_date_field = page.query_selector_all('[jscontroller="OKD1oe"] [aria-label="Departure"]')[0]
    time.sleep(0.4)
    departure_date_field.fill(depart_date)
    page.keyboard.press('Tab')
    time.sleep(0.4)

    # type "Return date"
    return_date_field = page.query_selector_all('[jscontroller="OKD1oe"] [aria-label="Return"]')[0]
    time.sleep(0.4)
    return_date_field.fill(return_date)
    page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    time.sleep(3)

    # press "More flights"
    page.query_selector('.zISZ5c button').click()
    time.sleep(2)

    parser = LexborHTMLParser(page.content())
    page.close()

    return parser

def scrape_google_flights(parser):
    data = {}
    major_airlines = ["American", "Delta", "United", "Southwest", "Alaska", "JetBlue"]

    categories = parser.root.css('.zBTtmb')
    category_results = parser.root.css('.Rk10dc')

    print("Debug: Number of categories found:", len(categories))

    for category, category_result in zip(categories, category_results):
        category_data = []
        print(f"Debug: Processing category: {category.text()}")

        for result in category_result.css('.yR1fYc'):
            company_element = result.css_first('.Ir0Voe .sSHqwe')
            stops_element = result.css_first('.EfT7Ae .ogfYpf')
            
            if company_element and stops_element:
                company = company_element.text()
                stops = stops_element.text()
                
                print(f"Debug: Airline: {company}, Stops: {stops}")
                
                # Check if any major airline name is in the company string
                is_major_airline = any(airline.lower() in company.lower() for airline in major_airlines)
                has_few_stops = stops == "Nonstop" or "1 stop" in stops
                
                if is_major_airline and has_few_stops:
                    date = result.css('[jscontroller="cNtv4b"] span')
                    depart_date = date[0].text() if len(date) > 0 else "N/A"
                    arrival_date = date[1].text() if len(date) > 1 else "N/A"
                    duration = result.css_first('.AdWm1c.gvkrdb').text() if result.css_first('.AdWm1c.gvkrdb') else "N/A"
                    emissions = result.css_first('.V1iAHe .AdWm1c').text() if result.css_first('.V1iAHe .AdWm1c') else "N/A"
                    emission_comparison = result.css_first('.N6PNV').text() if result.css_first('.N6PNV') else "N/A"
                    price = result.css_first('.U3gSDe .FpEdX span').text() if result.css_first('.U3gSDe .FpEdX span') else "N/A"
                    price_type = result.css_first('.U3gSDe .N872Rd').text() if result.css_first('.U3gSDe .N872Rd') else "N/A"

                    flight_data = {
                        'departure_date': depart_date,
                        'arrival_date': arrival_date,
                        'company': company,
                        'duration': duration,
                        'stops': stops,
                        'emissions': emissions,
                        'emission_comparison': emission_comparison,
                        'price': price,
                        'price_type': price_type
                    }

                    airports = result.css_first('.Ak5kof .sSHqwe')
                    service = result.css_first('.hRBhge')

                    if service:
                        flight_data['service'] = service.text()
                    elif airports:
                        departure_airport = airports.css_first('span:nth-child(1) .eoY5cb')
                        arrival_airport = airports.css_first('span:nth-child(2) .eoY5cb')
                        flight_data['departure_airport'] = departure_airport.text() if departure_airport else "N/A"
                        flight_data['arrival_airport'] = arrival_airport.text() if arrival_airport else "N/A"

                    category_data.append(flight_data)
                    print("Debug: Flight added to results")
                else:
                    print("Debug: Flight not added (not a major airline or too many stops)")
            else:
                print("Debug: Could not find company or stops information")

        data[category.text().lower().replace(' ', '_')] = category_data
        print(f"Debug: Added {len(category_data)} flights to category {category.text()}")

    print("Debug: Total categories in result:", len(data))
    return data