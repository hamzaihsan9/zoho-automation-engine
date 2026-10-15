"""
ZohoPulse - Intelligent Zoho CRM & Books Automation Engine
FastAPI application serving dashboard views, API simulator, and Deluge studio.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import db, Lead, Deal, Invoice
from app.deluge_engine import DelugeEngine
from app.zoho_client import zoho_client

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "deluge"

app = FastAPI(
    title="ZohoPulse CRM Automation Engine",
    description="Enterprise-grade Zoho CRM & Books Lead-to-Cash Automation Platform",
    version="2.4.0"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Deluge Scripts Catalog Metadata
DELUGE_CATALOG = [
    {
        "filename": "1_lead_ingestion_and_dedup.dg",
        "purpose": "Web-to-Lead Ingestion, Deduplication by Email/Phone, and Field Normalization",
        "trigger": "Zoho CRM Webhook or Web-to-Lead form submission",
        "tasks_used": ["zoho.crm.searchRecords", "zoho.crm.updateRecord", "zoho.crm.createRecord"],
    },
    {
        "filename": "2_ai_lead_scoring_and_assignment.dg",
        "purpose": "Multi-Factor Qualification Scoring (0-100 pts) and Round-Robin Sales Rep Assignment",
        "trigger": "Zoho CRM Workflow Rule on Lead Creation / Edit",
        "tasks_used": ["zoho.crm.getRecordById", "zoho.crm.updateRecord"],
    },
    {
        "filename": "3_deal_conversion_workflow.dg",
        "purpose": "Automated Lead Conversion into Account, Contact, and Opportunity Deal records",
        "trigger": "Zoho CRM Blueprint Transition 'Qualified / Convert'",
        "tasks_used": ["zoho.crm.searchRecords", "zoho.crm.createRecord(Accounts)", "zoho.crm.createRecord(Contacts)", "zoho.crm.createRecord(Deals)"],
    },
    {
        "filename": "4_auto_invoice_generator_books.dg",
        "purpose": "Automated Deal-to-Invoice Generation in Zoho Books with line items and sales tax",
        "trigger": "Zoho CRM Workflow Rule on Deal Stage 'Closed Won'",
        "tasks_used": ["zoho.crm.getRecordById", "zoho.books.createRecord(Invoices)", "zoho.crm.updateRecord"],
    },
    {
        "filename": "5_webhook_notification_dispatcher.dg",
        "purpose": "Outbound Secure Webhook Dispatcher with HMAC-SHA256 Signatures",
        "trigger": "Custom Function / Scheduled Action on CRM Event Dispatch",
        "tasks_used": ["invokeurl", "zoho.encryption.hmacSha256"],
    }
]

def load_deluge_script(filename: str) -> Dict[str, Any]:
    file_path = SCRIPTS_DIR / filename
    if not file_path.exists():
        return {"filename": filename, "lines": ["// Script not found."], "content": ""}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    meta = next((item for item in DELUGE_CATALOG if item["filename"] == filename), {
        "filename": filename,
        "purpose": "Custom Deluge Automation",
        "trigger": "Zoho CRM Workflow",
        "tasks_used": ["zoho.crm.*"]
    })
    return {**meta, "lines": lines, "content": content}

# ==============================================================================
# HTML VIEW ROUTES
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    leads = list(db.leads.values())
    deals = list(db.deals.values())
    invoices = list(db.invoices.values())
    
    total_pipeline = sum(d.amount for d in deals if d.stage != "Closed Lost")
    total_invoiced = sum(i.total for i in invoices)

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "active_tab": "dashboard",
        "leads": leads,
        "deals": deals,
        "invoices": invoices,
        "total_pipeline_val": total_pipeline,
        "total_invoiced_val": total_invoiced,
        "webhook_logs": db.webhook_logs
    })

@app.get("/leads", response_class=HTMLResponse)
async def leads_view(request: Request):
    leads = list(db.leads.values())
    return templates.TemplateResponse(request=request, name="leads.html", context={
        "active_tab": "leads",
        "leads": leads
    })

@app.get("/deals", response_class=HTMLResponse)
async def deals_view(request: Request):
    deals = list(db.deals.values())
    total_pipeline = sum(d.amount for d in deals if d.stage != "Closed Lost")
    return templates.TemplateResponse(request=request, name="deals.html", context={
        "active_tab": "deals",
        "deals": deals,
        "total_pipeline_val": total_pipeline
    })

@app.get("/invoices", response_class=HTMLResponse)
async def invoices_view(request: Request):
    invoices = list(db.invoices.values())
    total_invoiced = sum(i.total for i in invoices)
    return templates.TemplateResponse(request=request, name="invoices.html", context={
        "active_tab": "invoices",
        "invoices": invoices,
        "total_invoiced_val": total_invoiced
    })

@app.get("/deluge-studio", response_class=HTMLResponse)
async def deluge_studio_view(request: Request, script: str = "1_lead_ingestion_and_dedup.dg"):
    current_script = load_deluge_script(script)
    return templates.TemplateResponse(request=request, name="deluge_studio.html", context={
        "active_tab": "deluge",
        "scripts": DELUGE_CATALOG,
        "current_script": current_script,
        "test_result": None
    })

@app.get("/api-console", response_class=HTMLResponse)
async def api_console_view(request: Request, endpoint: str = "crm_leads"):
    token_info = zoho_client.oauth.get_valid_token()
    
    if endpoint == "crm_deals":
        sim_response = zoho_client.simulate_crm_call("Deals", method="GET")
        data_payload = {"data": [d.dict() for d in db.deals.values()]}
    elif endpoint == "books_invoices":
        sim_response = zoho_client.simulate_crm_call("invoices", method="GET")
        sim_response["url"] = "https://books.zoho.com/api/v3/invoices"
        data_payload = {"code": 0, "message": "success", "invoices": [i.dict() for i in db.invoices.values()]}
    else:
        sim_response = zoho_client.simulate_crm_call("Leads", method="GET")
        data_payload = {"data": [l.dict() for l in db.leads.values()]}

    return templates.TemplateResponse(request=request, name="api_console.html", context={
        "active_tab": "api",
        "active_endpoint": endpoint,
        "token_info": token_info,
        "api_response": sim_response,
        "api_json_pretty": json.dumps(data_payload, indent=2, default=str)
    })

@app.get("/interview-guide", response_class=HTMLResponse)
async def interview_guide_view(request: Request):
    return templates.TemplateResponse(request=request, name="interview_guide.html", context={
        "active_tab": "interview"
    })

# ==============================================================================
# ACTION API ENDPOINTS
# ==============================================================================

@app.post("/api/leads/ingest")
async def ingest_lead_action(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    company: str = Form(...),
    annual_revenue: float = Form(0.0),
    lead_source: str = Form("ZohoPulse Web Portal")
):
    lead, telemetry = DelugeEngine.execute_lead_ingestion_and_scoring({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "company": company,
        "annual_revenue": annual_revenue,
        "lead_source": lead_source
    })
    return RedirectResponse(url="/leads", status_code=303)

@app.post("/api/leads/{lead_id}/convert")
async def convert_lead_action(lead_id: int):
    deal, telemetry = DelugeEngine.execute_lead_conversion_to_deal(lead_id)
    return RedirectResponse(url="/deals", status_code=303)

@app.post("/api/deals/{deal_id}/close-won")
async def close_won_deal_action(deal_id: int):
    invoice, telemetry = DelugeEngine.execute_deal_closed_won_to_invoice(deal_id)
    return RedirectResponse(url="/invoices", status_code=303)

@app.post("/api/oauth/refresh")
async def refresh_oauth_token_action():
    zoho_client.oauth.refresh_access_token()
    return RedirectResponse(url="/api-console", status_code=303)

@app.post("/api/deluge/test-run")
async def deluge_test_run(request: Request, script_filename: str = Form(...)):
    # Run test execution based on script
    if "lead_ingestion" in script_filename or "ai_lead_scoring" in script_filename:
        lead, telemetry = DelugeEngine.execute_lead_ingestion_and_scoring({
            "first_name": "Sandbox",
            "last_name": "Test Prospect",
            "email": "test.prospect@techcorp.pk",
            "phone": "+92-300-9998877",
            "company": "TechCorp Pakistan",
            "annual_revenue": 750000.0,
            "lead_source": "Inbound Webhook"
        })
    elif "deal_conversion" in script_filename:
        first_lead = next(iter(db.leads.values()))
        deal, telemetry = DelugeEngine.execute_lead_conversion_to_deal(first_lead.id)
    elif "auto_invoice" in script_filename:
        first_deal = next(iter(db.deals.values()))
        inv, telemetry = DelugeEngine.execute_deal_closed_won_to_invoice(first_deal.id)
    else:
        log = DelugeEngine.dispatch_webhook("test.simulation", {"timestamp": "2026-10-15T12:00:00Z"})
        telemetry = {
            "execution_time_ms": 14.2,
            "statements_evaluated": 18,
            "logs": [f"[DELUGE::INFO] Dispatched webhook event 'test.simulation' with signature {log.signature}"],
            "status": "DELIVERED"
        }

    current_script = load_deluge_script(script_filename)
    return templates.TemplateResponse(request=request, name="deluge_studio.html", context={
        "active_tab": "deluge",
        "scripts": DELUGE_CATALOG,
        "current_script": current_script,
        "test_result": telemetry
    })

# Webhook listener endpoint
@app.post("/v1/webhooks/crm-events")
async def incoming_webhook_receiver(payload: Dict[str, Any]):
    return JSONResponse(content={"status": "acknowledged", "received_at": "2026-10-15T12:00:00Z"})
