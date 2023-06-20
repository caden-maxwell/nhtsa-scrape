from . import WebRequestHandler


def get_search_info():
    request_handler = WebRequestHandler()
    url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search"
    request_handler.queue_url(url)

    request_handler.send_requests()
    responses = request_handler.get_responses()

    return responses