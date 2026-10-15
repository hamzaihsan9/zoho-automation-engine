"""
ZohoPulse Data Models
Provides in-memory and persistent SQLite data structures for Zoho CRM & Books entities.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Lead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    company: str
    annual_revenue: float
    lead_source: str
    lead_score: int = 0
    lead_classification: str = "Cold"
    lead_status: str = "New / Unassigned"
    assigned_rep: str = "Unassigned"
    score_breakdown: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Deal(BaseModel):
    id: int
    deal_name: str
    account_name: str
    contact_name: str
    amount: float
    stage: str  # "Qualification", "Needs Analysis", "Proposal / Value Proposition", "Negotiation / Review", "Closed Won", "Closed Lost"
    probability: int
    closing_date: str
    owner: str
    lead_id: Optional[int] = None
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvoiceLineItem(BaseModel):
    name: str
    description: str
    rate: float
    quantity: int
    amount: float

class Invoice(BaseModel):
    id: int
    invoice_number: str
    deal_id: int
    customer_name: str
    date: str
    due_date: str
    line_items: List[InvoiceLineItem]
    subtotal: float
    tax_amount: float
    total: float
    status: str = "Sent"  # Draft, Sent, Paid, Overdue
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookLog(BaseModel):
    id: int
    event_type: str
    source: str
    destination: str
    payload: Dict[str, Any]
    status: str
    signature: str
    timestamp: str

# In-Memory Database Store with pre-loaded realistic B2B enterprise records
class DataStore:
    def __init__(self):
        self.leads: Dict[int, Lead] = {}
        self.deals: Dict[int, Deal] = {}
        self.invoices: Dict[int, Invoice] = {}
        self.webhook_logs: List[WebhookLog] = []
        self._lead_counter = 100
        self._deal_counter = 500
        self._invoice_counter = 1000
        self._log_counter = 1
        self._seed_data()

    def _seed_data(self):
        # Seed initial realistic Leads
        l1 = Lead(
            id=101,
            first_name="Asad",
            last_name="Qureshi",
            email="asad.qureshi@agritech-cloud.pk",
            phone="+92-300-8451122",
            company="AgriTech Cloud Pakistan",
            annual_revenue=1200000.0,
            lead_source="Inbound Webhook",
            lead_score=95,
            lead_classification="Hot (High Priority)",
            lead_status="Sales Qualified (SQL)",
            assigned_rep="Hamza Ihsan (Account Executive)",
            score_breakdown=[
                "Enterprise Budget Tier (>= $1M): +40 pts",
                "Complete Contact (Email + Phone): +20 pts",
                "High Intent Channel (Inbound Webhook): +25 pts",
                "Verified Corporate Email Domain: +15 pts"
            ]
        )
        l2 = Lead(
            id=102,
            first_name="Zoya",
            last_name="Mirza",
            email="zoya.mirza@finovate.io",
            phone="+92-321-4567890",
            company="Finovate Payments Ltd",
            annual_revenue=350000.0,
            lead_source="Direct Demo Request",
            lead_score=80,
            lead_classification="Hot (High Priority)",
            lead_status="Sales Qualified (SQL)",
            assigned_rep="Sarah Chen (Enterprise Rep)",
            score_breakdown=[
                "Mid-Market Tier ($250k - $1M): +25 pts",
                "Complete Contact (Email + Phone): +20 pts",
                "High Intent Channel: +25 pts",
                "Verified Corporate Email Domain: +15 pts"
            ]
        )
        l3 = Lead(
            id=103,
            first_name="Bilal",
            last_name="Siddiqui",
            email="bilal@desigardens.org",
            phone="+92-333-9876543",
            company="Desi Gardens & Nursery",
            annual_revenue=65000.0,
            lead_source="Organic Search",
            lead_score=65,
            lead_classification="Warm (Nurture)",
            lead_status="Marketing Qualified (MQL)",
            assigned_rep="Tariq Mehmood (Mid-Market Specialist)",
            score_breakdown=[
                "Growth Tier ($50k - $250k): +15 pts",
                "Complete Contact (Email + Phone): +20 pts",
                "Inbound Organic: +15 pts",
                "Verified Corporate Domain: +15 pts"
            ]
        )
        self.leads[l1.id] = l1
        self.leads[l2.id] = l2
        self.leads[l3.id] = l3

        # Seed initial Deals
        d1 = Deal(
            id=501,
            deal_name="AgriTech Cloud - Zoho Enterprise CRM Suite",
            account_name="AgriTech Cloud Pakistan",
            contact_name="Asad Qureshi",
            amount=28500.0,
            stage="Proposal / Value Proposition",
            probability=60,
            closing_date=(date.today() + timedelta(days=20)).isoformat(),
            owner="Hamza Ihsan (Account Executive)",
            lead_id=101
        )
        d2 = Deal(
            id=502,
            deal_name="Finovate - Zoho Books & Inventory Automation",
            account_name="Finovate Payments Ltd",
            contact_name="Zoya Mirza",
            amount=18000.0,
            stage="Closed Won",
            probability=100,
            closing_date=(date.today() - timedelta(days=2)).isoformat(),
            owner="Sarah Chen (Enterprise Rep)",
            lead_id=102,
            invoice_id="INV-90214",
            invoice_number="INV-2026-001"
        )
        self.deals[d1.id] = d1
        self.deals[d2.id] = d2

        # Seed initial generated Invoice (from Closed Won deal)
        inv1 = Invoice(
            id=1001,
            invoice_number="INV-2026-001",
            deal_id=502,
            customer_name="Finovate Payments Ltd",
            date=(date.today() - timedelta(days=2)).isoformat(),
            due_date=(date.today() + timedelta(days=13)).isoformat(),
            line_items=[
                InvoiceLineItem(
                    name="Finovate - Zoho Books & Inventory Automation",
                    description="Annual SaaS Platform License & Support SLA",
                    rate=15300.0,
                    quantity=1,
                    amount=15300.0
                ),
                InvoiceLineItem(
                    name="Enterprise Setup & Onboarding",
                    description="Dedicated solutions architect & CRM sync deployment",
                    rate=2700.0,
                    quantity=1,
                    amount=2700.0
                )
            ],
            subtotal=18000.0,
            tax_amount=2880.0,  # 16% sales tax
            total=20880.0,
            status="Sent"
        )
        self.invoices[inv1.id] = inv1

        # Seed initial Webhook Log
        log1 = WebhookLog(
            id=1,
            event_type="deal.closed_won",
            source="Zoho CRM Deluge Engine",
            destination="https://api.zohopulse.io/v1/webhooks/crm-events",
            payload={"deal_id": 502, "deal_name": d2.deal_name, "amount": 18000.0, "invoice_id": "INV-90214"},
            status="delivered (HTTP 200)",
            signature="a9f4c3b281e7d4469019b7d82e1c94a558b901fc82d3e",
            timestamp=datetime.utcnow().isoformat()
        )
        self.webhook_logs.append(log1)

    def next_lead_id(self) -> int:
        self._lead_counter += 1
        return self._lead_counter

    def next_deal_id(self) -> int:
        self._deal_counter += 1
        return self._deal_counter

    def next_invoice_id(self) -> int:
        self._invoice_counter += 1
        return self._invoice_counter

    def next_log_id(self) -> int:
        self._log_counter += 1
        return self._log_counter

db = DataStore()
