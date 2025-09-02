# **Playwright Product Scraper** 🕵️‍♂️

An **automated product scraper** built using **Python** + **Playwright** to extract product details from an inventory-based website.  
It supports **infinite scrolling**, **session persistence**, and exports data to `products.json`.

---

## **📂 Project Structure**
playwright-product-scraper/
├── README.md                 # 📘 Project documentation
├── requirements.txt          # 📦 Python dependencies
├── .gitignore                # 🚫 Ignored files (e.g., storage_state.json, .env, __pycache__)
├── .env                      # 🔑 Environment variables (not committed)
│
├── config/
│   ├── settings.yaml         # 🌐 Base URLs & configuration
│   └── selectors.yaml        # 🎯 All CSS selectors & locators
│
├── data/
│   ├── output/
│   │   └── products.json     # 🛒 Exported product data (auto-generated)
│   └── storage_state.json    # 🔐 Saved browser session (auto-generated)
│
├── src/
│   ├── main.py               # 🚀 Entry point — orchestrates the scraper
│   ├── auth.py               # 🔑 Handles login & session management
│   ├── scrape.py             # 🕵️ Scraping logic + infinite scroll
│   ├── utils.py              # 🛠️ Helper functions, logging, waits
│
└── tests/
    └── test_smoke.py         # ✅ Smoke tests for core scraping flow



yaml
Copy code

---

## **⚡ Features**
✅ **Automated Login** → Uses session storage (`storage_state.json`) to avoid repeated logins  
✅ **Infinite Scrolling** → Dynamically loads all products  
✅ **Data Export** → Saves extracted products into `data/output/products.json`  
✅ **Configurable** → Centralized selectors & URLs in YAML  
✅ **Session Persistence** → Speeds up repeated runs  
✅ **Tested** → Includes a smoke test for validation  

---

## **🛠️ Installation & Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/playwright-product-scraper.git
cd playwright-product-scraper
2. Create & Activate Virtual Environment
bash
Copy code
python -m venv .venv
source .venv/bin/activate     # On Mac/Linux
.venv\Scripts\activate        # On Windows
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
🔑 Configure Environment Variables
Create a .env file in the project root:

env
Copy code
BASE_URL=https://example.com
APP_USERNAME=your_username
APP_PASSWORD=your_password
⚠️ Note: .env is ignored in git for security reasons.

🚀 Running the Scraper
Run the main scraper:

bash
Copy code
python -m src.main
Optional Arguments
Argument	Description	Example
--force-login	Forces fresh login (ignores session)	python -m src.main --force-login
--output	Custom JSON output path	python -m src.main --output data/products.json

🧪 Running Tests
Run smoke tests using pytest:

bash
Copy code
pytest tests/test_smoke.py -s -v
This test will:

Log in to the website (or reuse session)

Navigate to the inventory

Scrape products

Verify correct structure of the output

📦 Output
After running the scraper, results are saved at:

bash
Copy code
data/output/products.json
Example of extracted product data:

json
Copy code
[
  {
    "id": "P1234",
    "title": "Men's Casual Shirt",
    "category": "Clothing",
    "cost": "$25",
    "inventory": "In Stock",
    "weight_kg": "0.5",
    "composition": "100% Cotton",
    "updated": "2025-09-02"
  }
]
🗝️ Session Management
First run → logs in using credentials from .env

Saves session to:

bash
Copy code
data/storage_state.json
On future runs, Playwright reuses the session for faster scraping

Use --force-login to bypass the saved session

📌 Notes
Make sure to activate your virtual environment before running.

Keep your .env secure — never commit it.

If scraping slows down, increase scroll speed in scrape.py.

👨‍💻 Author
💼 GitHub: BluePrisoner



