
response = map_client.places_nearby(
        location = location,
        keyword = search_string,
        name = 'cafe',
        radius=distance
    )

business_list.extend(response.get('results'))
cafe = []