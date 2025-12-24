# Family Wealth AI

A LINE OA Chatbot for Thai family wealth management using Gemini AI + Google Sheets.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- LINE Official Account with Messaging API enabled
- Google Cloud project with Sheets API enabled
- Gemini API key

### 2. Setup

```bash
# Clone and navigate to project
cd opes-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in credentials
cp .env.example .env
```

### 3. Configure Google Sheets

1. Create an empty Google Sheet
2. Share it with your service account email (Editor access)
3. Copy the Sheet ID from the URL and add to `.env`
4. Run the setup script:

```bash
python3 scripts/setup_sheets.py
```

This creates all required tabs with proper headers:

| Sheet Name | Key Columns |
|------------|-------------|
| **Users** | user_id, display_name, monthly_budget, target_allocation |
| **Transactions** | asset (normalized), asset_raw (original), asset_type, currency, total_thb |
| **Asset_Reference** | asset_symbol, current_price_thb |
| **Watchlist_Alerts** | asset_symbol, risk_status |

### 4. Configure LINE Webhook

1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Set Webhook URL to your endpoint: `https://your-domain.com/webhook`
3. Enable "Use webhook"
4. Disable "Auto-reply messages"

### 5. Run Locally

```bash
# Start the development server
python main.py

# In another terminal, expose with ngrok
ngrok http 8080
```

### 6. Deploy to Cloud Functions

```bash
gcloud functions deploy family-wealth-ai \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point main \
  --set-env-vars "LINE_CHANNEL_ACCESS_TOKEN=xxx,LINE_CHANNEL_SECRET=xxx,GOOGLE_SHEETS_ID=xxx,GEMINI_API_KEY=xxx"
```

## 📸 How It Works

1. **Send a screenshot** of your Dime! or Binance trade confirmation
2. **Gemini Vision** extracts: Asset, Side (Buy/Sell), Amount, Price
3. **Data is saved** to Google Sheets automatically
4. **Get a confirmation** with transaction details

## 🗂 Project Structure

```
opes-ai/
├── main.py                 # Cloud Function entry point
├── config.py               # Environment configuration
├── handlers/
│   ├── message_handler.py  # Text message routing
│   └── image_handler.py    # Screenshot processing
├── services/
│   ├── sheets_service.py   # Google Sheets CRUD
│   ├── gemini_service.py   # Gemini Vision + Text
│   └── line_service.py     # LINE API wrapper
├── models/
│   ├── user.py             # User model
│   └── transaction.py      # Transaction model
└── utils/
    └── flex_messages.py    # LINE Flex templates
```

## 📝 Commands

| Command | Description |
|---------|-------------|
| `help` / `ช่วยเหลือ` | Show help information |
| `status` / `สถานะ` | View portfolio holdings |
| `plan` / `แผน` | Smart DCA calculator (coming soon) |

## 🔮 Roadmap

- [x] Phase 1: Screenshot parsing with Gemini Vision
- [ ] Phase 2: Smart DCA Calculator
- [ ] Phase 2: Performance Dashboard with P/L
- [ ] Phase 3: Quarterly Rebalance Alerts
- [ ] Phase 3: Deep Research Watchdog
