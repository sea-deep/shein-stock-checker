# SHEIN Stock Checker

Checks the SHEIN Men category periodically and sends a Telegram alert when stock count reaches a threshold (100+ by default).

## Prerequisites

- Linux with Google Chrome installed (headless is used)
- Python 3.10+ (project venv included)
- Telegram bot token and chat ID

## Setup

1. Create a `.env` file next to `check_stock.py` with:

	```env
	TELEGRAM_BOT_TOKEN=xxxx:yyyy
	TELEGRAM_CHAT_ID=123456789
	```

2. Activate the virtual environment and install dependencies:

	```bash
	# optional: if not already using the workspace venv
	source venv/bin/activate
	pip install -r requirements.txt
	```

## Run

```bash
/home/deepak/code/shein/venv/bin/python check_stock.py
```

It will refresh every 60 seconds and post to Telegram when stock >= 100.

## Notes

- WebDriver is auto-managed by `webdriver-manager`; no manual chromedriver setup needed.
- If VS Code shows missing import warnings, ensure the interpreter is set to this workspace venv.
- You can change the alert threshold in `check_stock.py` if needed.
