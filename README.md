# OtakLabs Certificate Builder - IDMC (Indahnya Dhamma Meditation Community)

<img src="logo_IDMC.jpeg" alt="Logo IDMC" width="200" />

This repository contains all the assets needed to:

1. Consolidate Muse recordings from before and after a workshop.
2. Generate workshop certificates.

## Instructions

1. Take whole-screen screenshots from Muse screens.
    - This will work with/without the powerbands section expanded.
    - No need to scroll the powerband section to show the Gamma legend.
2. Copy all screenshots to `1.process_screenshots/Muse results - raw`.
3. Run `process_screenshots.py` script. This will produce processed images in `1.process_screenshots/Muse results - output`.
4. Create a Google Sheets `Muse Results`. It should have at least these 2 sheets:
    - `1. Cleaned`
    - `2. Cleaned + Name corrected`
    - Optional sheets like `3. Merged (raw)`, `3. Merged`, and `Stats` may also be created.
5. Import `1.process_screenshots/Muse results - output/session_data.csv` to `Muse Results` Sheets, sheet `1. Cleaned`.
    - Clean the data e.g. missing or incorrect values.
6. Make a copy from `1. Cleaned` to `2. Cleaned + Name corrected`.
    - Correct all the names.
7. Copy produced images directory `1.process_screenshots/Muse results - output` to `3.create_certificates/Muse outputs - processed`
    - Update the screenshots and their names as necessary.
8. Download the following sheets from the Google Sheets document:
    - `1. Cleaned` to `2.prepare_date/session_data_cleaned.csv`
    - `2. Cleaned + Name corrected` to `2.prepare_data/session_data_cleaned_and_name_corrected.csv`
9. Run `2.prepare_data/merge.py`. This should produce a file `2.prepare_data/session_data_merged.csv`.
10. (Optional) Import `2.prepare_data/session_data_merged.csv` to the `3. Merged (raw)` sheet.
11. Copy page 1 of the certificates to `3.create_certificates/certificates-page1`.
    - Each certificate should have the same name as the recipient's full name, without period characters (`.`).
    - **Assume there is no duplicate full names**. TODO: Improve the system when there are duplicate full names.
12. Run `3.create_certificates/create_certificates.py`.
    - This should produce certificates that combines images from `certificates-page1` and `Muse outputs - processed` directories.
    - The final results are stored in the `certificates` directory.