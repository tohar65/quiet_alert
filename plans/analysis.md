# Analysis of Alert Fetching Logic

## Current Implementation (`oref_alert_parser/parser.py`)
- **Endpoint:** `https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json`
- **Headers:**
    - `User-Agent`: Desktop Windows Chrome 58
    - `Referer`: `https://www.oref.org.il/`
    - `X-Requested-With`: `XMLHttpRequest`
    - `Accept-Encoding`: `gzip, deflate`
- **Logic:**
    - Fetches the JSON.
    - Manually handles gzip decompression (checks header or tries to decompress).
    - Decodes `utf-8-sig` to handle BOM.
    - Returns empty list on error.

## HAR File Analysis (`records_from_website/www.oref.org.il.har`)
- **Endpoint:** `https://www.oref.org.il/warningMessages/alert/History/AlertsHistory.json` (Case sensitivity might matter, though usually not for domain/path on IIS, but good to match).
- **Headers (Successful Request):**
    - `User-Agent`: Mobile Android Chrome 145
    - `Referer`: `https://www.oref.org.il/heb/alerts-history`
    - `sec-ch-ua-platform`: `"Android"`
    - `sec-ch-ua-mobile`: `?1`
    - `Accept`: `application/json, text/plain, */*`
    - **Note:** `X-Requested-With` is NOT present in the HAR request headers.

## Gaps & Improvements
1.  **Headers Mismatch:** The current code uses a desktop User-Agent and `X-Requested-With`, while the HAR shows a mobile User-Agent and *no* `X-Requested-With`. The `Referer` is also slightly different (`/` vs `/heb/alerts-history`).
2.  **Endpoint Case:** The code uses `WarningMessages` while HAR uses `warningMessages`. This is likely case-insensitive but matching the HAR is safer.
3.  **Modern Headers:** The HAR includes `sec-ch-ua` headers which are standard for modern Chrome.
4.  **Error Handling:** The current code swallows errors and returns empty list. It might be better to log more details or retry.

## Plan
1.  Update `oref_alert_parser/parser.py` to use the headers found in the HAR file.
2.  Update the URL to match the case in the HAR file.
3.  Remove `X-Requested-With` as it's not in the HAR.
4.  Add `sec-ch-ua` headers.
5.  Keep the gzip/BOM handling as it seems robust.
