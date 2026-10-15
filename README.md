# ZohoPulse: B2B Lead-to-Cash Automation Engine

ZohoPulse is a full-stack enterprise automation suite integrating Zoho CRM and Zoho Books using proprietary Zoho Deluge scripting and REST APIs. The platform automates the end-to-end B2B revenue lifecycle from inbound lead ingestion and deduplication to automated opportunity conversion, sales qualification scoring, and Zoho Books invoice generation.

---

## Architecture Overview

The system bridges customer acquisition and financial operations through an event-driven architecture powered by five production Zoho Deluge custom functions:

1. Web-to-Lead Ingestion and Deduplication (1_lead_ingestion_and_dedup.dg):
   Intercepts incoming lead payloads, normalizes contact data, and searches Zoho CRM by email and phone criteria to prevent duplicate clutter. Existing records are updated with activity timestamps; new records are created with initial tracking tags.

2. Multi-Factor Qualification Scoring (2_ai_lead_scoring_and_assignment.dg):
   Calculates an automated qualification score (0 to 100 points) based on annual revenue tiers, contact completeness, channel intent, and corporate domain verification. Implements a round-robin assignment algorithm distributing leads evenly across Account Executives.

3. Automated Lead-to-Deal Conversion (3_deal_conversion_workflow.dg):
   Executes upon lead qualification, creating or linking an Account entity, generating an associated Contact, and opening a new Opportunity Deal in the CRM pipeline with calculated closing dates.

4. Deal-to-Invoice Generation (4_auto_invoice_generator_books.dg):
   Triggers automatically when a deal transitions to "Closed Won". Calls zoho.books.createRecord() to generate an itemized invoice in Zoho Books, calculating subtotal, 16% corporate sales tax, and Net-15 payment terms before dispatching client notifications.

5. Outbound Webhook Dispatcher (5_webhook_notification_dispatcher.dg):
   Dispatches signed webhook event payloads to external enterprise portals using the Deluge invokeurl task, securing deliveries with HMAC-SHA256 signatures.

---

## Technical Stack

- Backend Engine: Python 3.12+ with FastAPI and Uvicorn
- Cloud Scripting: Zoho Deluge 2.0 (CRM and Books built-in tasks)
- Authentication: Zoho Accounts OAuth 2.0 (Authorization Code and Refresh Token rotation)
- API Integration: Zoho CRM REST API v2, Zoho Books REST API v3
- Frontend: Responsive HTML5 with Tailwind CSS and Jinja2 templating
- Execution Telemetry: In-memory runtime logging with latency measurement in milliseconds

---

## Project Structure

```
zohopulse-crm-engine/
├── app/
│   ├── main.py              # FastAPI server routes, dashboard controllers, and API simulator
│   ├── models.py            # Pydantic data schemas for Leads, Deals, Invoices, and Webhooks
│   ├── deluge_engine.py     # Deluge execution engine with statement evaluation telemetry
│   ├── zoho_client.py       # Zoho OAuth 2.0 manager and REST API v2 connector
│   └── templates/
│       ├── base.html        # Main layout with ecosystem navigation and token monitor
│       ├── dashboard.html   # Executive KPI overview and pipeline metrics
│       ├── leads.html       # CRM Leads catalog with scoring breakdowns
│       ├── deals.html       # Deals Kanban pipeline with one-click conversion
│       ├── invoices.html    # Itemized Zoho Books invoices
│       ├── deluge_studio.html # Syntax-highlighted code inspector and sandbox runner
│       ├── api_console.html # OAuth 2.0 token manager and REST API explorer
│       └── interview_guide.html # Comprehensive Zoho technical interview guide
├── scripts/
│   └── deluge/
│       ├── 1_lead_ingestion_and_dedup.dg
│       ├── 2_ai_lead_scoring_and_assignment.dg
│       ├── 3_deal_conversion_workflow.dg
│       ├── 4_auto_invoice_generator_books.dg
│       └── 5_webhook_notification_dispatcher.dg
├── run.py                   # Server startup script
└── README.md
```

---

## Setup and Execution

1. Navigate to the project directory:
   cd /home/kali/Projects/zohopulse-crm-engine

2. Launch the application:
   /home/kali/Projects/talentpulse-ai/venv/bin/python run.py

3. Open the platform in your browser:
   http://localhost:8090

4. Key Navigation Endpoints:
   - Dashboard: http://localhost:8090/
   - Leads and Scoring: http://localhost:8090/leads
   - Deals Pipeline: http://localhost:8090/deals
   - Zoho Books Invoices: http://localhost:8090/invoices
   - Deluge Script Studio: http://localhost:8090/deluge-studio
   - API and OAuth Console: http://localhost:8090/api-console
   - Interview Preparation Guide: http://localhost:8090/interview-guide

---

## License

This project is licensed under the MIT License.
