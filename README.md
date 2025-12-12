# SponsorCatcher

Auto-books sponsor slots on MHI website before they sell out.

## What it does

1. Logs into https://members.manufacturedhousing.org
2. Goes to sponsor page
3. Searches for the sponsor slot you want (e.g., "Attendee Giveaways")
4. Adds to cart
5. Fills payment details
6. Scrolls to submit button (you click manually, or enable auto-submit)

## Monitoring Mode

If the slot is sold out, enable monitoring:
- Keeps refreshing every X seconds
- When slot becomes available → immediately books it
- You can enable auto-submit to complete the purchase automatically

## How to run

```bash
# GUI mode (recommended)
uv run python main.py --gui

# CLI mode (needs .env and config.yaml in current dir)
uv run python main.py

# CLI with auto-submit (ACTUALLY PLACES ORDER)
uv run python main.py --submit
```

## Config locations

**Development (running from source):**
- `./config.yaml` - booking settings
- `./.env` - login credentials

**Packaged app:**
- macOS: `~/Library/Application Support/SponsorCatcher/config.yaml`
- Windows: `%APPDATA%/SponsorCatcher/config.yaml`

## Config format

**.env file:**
```
SPONSOR_EMAIL=your@email.com
SPONSOR_PASSWORD=yourpassword
```

**config.yaml:**
```yaml
search_keyword: "Attendee Giveaways"
payment:
  name_on_card: John Doe
  card_number: "4111111111111111"
  cvv: "123"
  exp_month: "12"
  exp_year: "2026"
  billing_zip: "33137"
  confirmation_email: your@email.com
```

## GUI Layout

### Configuration Tab
- Login credentials (email, password, sponsor URL)
- Search keyword (what sponsor slot to find)
- Payment details (card info)
- Save/Load buttons

### Run Automation Tab
- Log output with timestamps
- Monitoring toggle + interval setting
- Auto-submit checkbox (WARNING: actually places order!)
- Start/Stop buttons

## Flow diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      NORMAL MODE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Login → Sponsor Page → Search → Add to Cart → Checkout     │
│                                      ↓                      │
│                              Fill Payment Details           │
│                                      ↓                      │
│                              Scroll to Submit               │
│                                      ↓                      │
│                         (Manual submit or auto-submit)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MONITORING MODE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Login (once) ──────────────────────────────┐               │
│       ↓                                     │               │
│  ┌─────────────────────────────────────┐    │               │
│  │  Navigate to Sponsor Page           │    │               │
│  │           ↓                         │    │               │
│  │  Search for product                 │    │               │
│  │           ↓                         │    │               │
│  │  Check availability                 │    │               │
│  │           ↓                         │    │               │
│  │  SOLD OUT? ──Yes──→ Wait X seconds ─┼────┘               │
│  │     │                               │                    │
│  │    No (AVAILABLE!)                  │                    │
│  │     ↓                               │                    │
│  │  Run full booking workflow          │                    │
│  │     ↓                               │                    │
│  │  SUCCESS!                           │                    │
│  └─────────────────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Build for distribution

```bash
# Install pyinstaller
pip install pyinstaller

# Build executable
python build_exe.py --onefile

# Output:
# - Windows: dist/SponsorCatcher.exe
# - macOS: dist/SponsorCatcher.app
```

GitHub Actions automatically builds Windows installer + macOS DMG on tag push.

## Project structure

```
SponsorCatcher/
├── main.py                 # Entry point (--gui flag for GUI)
├── gui.py                  # GUI entry point for packaged app
├── build_exe.py            # PyInstaller build script
├── requirements.txt        # Dependencies
├── config.yaml             # Booking config (search + payment)
├── .env                    # Login credentials
└── src/sponsorcatcher/
    ├── config.py           # Config loading
    ├── browser.py          # Chrome driver setup
    ├── paths.py            # Platform-specific paths
    ├── locators/
    │   └── elements.py     # CSS/XPath selectors
    ├── pages/
    │   ├── base_page.py    # Base page utilities
    │   ├── login_page.py   # Login automation
    │   ├── sponsor_page.py # Search + add to cart
    │   ├── cart_page.py    # Cart + checkout
    │   └── checkout_page.py# Payment form
    ├── actions/
    │   └── booking.py      # Full booking workflow
    └── gui/
        ├── app.py          # Main window
        ├── config_tab.py   # Config form
        └── run_tab.py      # Automation controls
```

## Notes

- Browser stays visible (headed mode) so you can watch/intervene
- Images disabled for speed
- Password manager popups disabled
- Uses "eager" page load strategy (faster)
- All selectors use stable CSS classes, not auto-generated IDs
