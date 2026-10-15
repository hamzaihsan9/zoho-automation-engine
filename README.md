# Zoho Automation Engine

Enterprise Lead-to-Cash automation system integrating Zoho CRM and Zoho Books using Zoho Deluge scripting and REST APIs.

The engine automates revenue workflows including inbound lead deduplication, algorithmic lead qualification scoring, round-robin sales assignment, automated opportunity conversion, and Zoho Books invoice generation upon deal closing.

## Architecture

The workflow connects CRM customer acquisition to financial accounting across five Deluge custom functions:

1. Web-to-Lead Ingestion and Deduplication (1_lead_ingestion_and_dedup.dg)
   Normalizes inbound contact information and queries Zoho CRM by email and phone using searchRecords to prevent duplicate entries. Existing contacts receive updated activity timestamps; new contacts are provisioned with attribution tags.

2. Lead Qualification Scoring and Rep Assignment (2_ai_lead_scoring_and_assignment.dg)
   Scores incoming leads on a 0 to 100 point scale using enterprise revenue brackets, verified business email domains, and high-intent inbound channels. Qualified leads are distributed across Account Executives using modulo round-robin routing.

3. Opportunity Conversion Workflow (3_deal_conversion_workflow.dg)
   Converts sales-qualified leads into Zoho CRM Accounts, Contacts, and Opportunities with milestone closing dates and stage tracking.

4. Automated Invoicing in Zoho Books (4_auto_invoice_generator_books.dg)
   Triggers when a CRM opportunity reaches Closed Won. Calls the Zoho Books API to generate an itemized invoice with line items, applicable sales tax, and Net-15 payment terms.

5. Secure Webhook Notification Dispatcher (5_webhook_notification_dispatcher.dg)
   Transmits signed JSON payloads to downstream systems and ERPs using the Deluge invokeurl task, authenticated via HMAC-SHA256 headers.

## Tech Stack

- Backend: Python 3, FastAPI, Uvicorn
- Cloud Scripting: Zoho Deluge 2.0 (CRM and Books tasks)
- Authentication: Zoho Accounts OAuth 2.0 (Token refresh rotation)
- APIs: Zoho CRM REST API v2, Zoho Books REST API v3
- Frontend: HTML5, Tailwind CSS, Jinja2 Templates

## Directory Structure

```
zoho-automation-engine/
├── app/
│   ├── main.py              # Application controllers, API routes, and simulator
│   ├── models.py            # Data schemas for Leads, Deals, Invoices, Webhooks
│   ├── deluge_engine.py     # Deluge execution runtime with latency tracking
│   ├── zoho_client.py       # Zoho OAuth 2.0 manager and API client
│   └── templates/
│       ├── base.html        # Base navigation and OAuth token status
│       ├── dashboard.html   # Pipeline overview and funnel metrics
│       ├── leads.html       # CRM Lead management and scoring table
│       ├── deals.html       # Opportunity pipeline
│       ├── invoices.html    # Generated Zoho Books invoices
│       ├── deluge_studio.html # Deluge code inspector and test runner
│       ├── api_console.html # OAuth token manager and REST explorer
│       └── interview_guide.html # Technical reference and architectural Q&A
├── scripts/
│   └── deluge/
│       ├── 1_lead_ingestion_and_dedup.dg
│       ├── 2_ai_lead_scoring_and_assignment.dg
│       ├── 3_deal_conversion_workflow.dg
│       ├── 4_auto_invoice_generator_books.dg
│       └── 5_webhook_notification_dispatcher.dg
├── requirements.txt
├── run.py
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Quickstart

1. Clone the repository:
   ```bash
   git clone git@github.com:hamzaihsan9/zoho-automation-engine.git
   cd zoho-automation-engine
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   python run.py
   ```

4. Access the web interface at:
   http://localhost:8090

## Modules and Routes

- Dashboard: http://localhost:8090/
- Leads and Scoring: http://localhost:8090/leads
- Deals Pipeline: http://localhost:8090/deals
- Zoho Books Invoices: http://localhost:8090/invoices
- Deluge Script Studio: http://localhost:8090/deluge-studio
- API and OAuth Console: http://localhost:8090/api-console
- Interview Technical Guide: http://localhost:8090/interview-guide

## Deluge Script Deployment

To deploy these functions in a live Zoho environment:

1. Navigate to Zoho CRM Setup > Developer Hub > Functions.
2. Create a new function, select Deluge as the language, and paste the code from scripts/deluge/.
3. Configure Workflow Rules or Webhooks to trigger the functions on record create or stage transition events.
4. For Zoho Books integration, ensure your Zoho CRM - Zoho Books integration connection is authorized with the ZohoBooks.invoices.CREATE scope.

## License

This project is licensed under the MIT License.
