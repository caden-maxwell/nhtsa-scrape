[Back to Documentation Overview](README.md)

---

# To-Do

- Get CISS database working
    - Figure out a data-driven way to keep track of what params a scrape was performed with. This way, the scrape menu doesn't have to worry about exactly what the payload needs to look like. The scrape engine itself (whether it be NASS or CISS) will convert the scrape params into a payload. With this, we will also be able to save the params to be used later, for example, if we need to resume a scrape or rescrape a profile altogether.
- Add EDR information to case page
    - Either as fields or downloadable file
    - If downloadable, download pdf. If pdf not available, download cdrx.
    - Unfortunately, I will not be able to view the cdrx files, as they require a subscription to an expensive paid software service. So, my ability to do anything with those files ends there.
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
- Include link for each case
