pyinstaller --add-data app/resources/settings.json:app/resources --add-data app/resources/payload.json:app/resources -n NHTSA-Scrape --hide-console hide-early main.py
