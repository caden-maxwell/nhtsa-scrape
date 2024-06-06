[Back to Documentation Overview](README.md)

---

# To-Do

- Get CISS database working
    - Lots to do here...
- Add EDR information to case page
    - Either as fields or downloadable file
- Fix error that results from scraping images without a case selected
    - Could be fixed by:
        - Autoselect first case in list if nothing is selected
        - Block buttons until case is selected
- Fix dark/light themes in compiled app not working -- only the light theme is ever applied
    - Could be fixed by:
        - Nuitka instead of Pyinstaller?
        - Create custom stylesheet and change via settings
- Fix "Scraping..." issue when exited out of data viewer before scrape is finished
    - Scraping still continues and cases are saved, but the data viewer is not updated accordingly upon being opened again.
    - Could be fixed by:
        - Stopping scraping altogether, and optionally implementing a "Resume scrape" or "Re-scrape" functionality on the data viewer page.
- Fix empty fields in the data viewer summary tab
