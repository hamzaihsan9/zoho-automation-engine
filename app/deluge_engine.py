"""
Deluge Script Execution & Telemetry Engine
Simulates and executes Zoho Deluge script logic with real-time logging and execution telemetry.
"""

import time
import hashlib
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Tuple
from app.models import db, Lead, Deal, Invoice, InvoiceLineItem, WebhookLog

SALES_REPRESENTATIVES = [
    {"name": "Hamza Ihsan (Account Executive)", "id": "481029000018271001", "email": "hamza@zohopulse.io"},
    {"name": "Sarah Chen (Enterprise Rep)", "id": "481029000018271002", "email": "sarah@zohopulse.io"},
    {"name": "Tariq Mehmood (Mid-Market Specialist)", "id": "481029000018271003", "email": "tariq@zohopulse.io"}
]

class DelugeEngine:
    @staticmethod
    def execute_lead_ingestion_and_scoring(payload: Dict[str, Any]) -> Tuple[Lead, Dict[str, Any]]:
        """
        Executes scripts:
        - 1_lead_ingestion_and_dedup.dg
        - 2_ai_lead_scoring_and_assignment.dg
        """
        start_time = time.time()
        logs = []

        email = payload.get("email", "").strip().lower()
        phone = payload.get("phone", "").strip()
        first_name = payload.get("first_name", "").strip()
        last_name = payload.get("last_name", "Valued Prospect").strip()
        company = payload.get("company", "Independent").strip()
        annual_revenue = float(payload.get("annual_revenue", 0.0))
        lead_source = payload.get("lead_source", "ZohoPulse Web Portal")

        logs.append(f"[DELUGE::INFO] Starting Ingestion for Lead: {email}")

        # Check existing lead by email for deduplication
        existing_lead = None
        for l in db.leads.values():
            if l.email.lower() == email:
                existing_lead = l
                break

        # Calculate Score
        score = 0
        breakdown = []

        # Factor 1: Revenue Scale
        if annual_revenue >= 1000000:
            score += 40
            breakdown.append("Enterprise Budget Tier (>= $1M): +40 pts")
        elif annual_revenue >= 250000:
            score += 25
            breakdown.append("Mid-Market Tier ($250k - $1M): +25 pts")
        elif annual_revenue >= 50000:
            score += 15
            breakdown.append("Growth Tier ($50k - $250k): +15 pts")
        else:
            score += 5
            breakdown.append("Entry Tier: +5 pts")

        # Factor 2: Contact Completeness
        if email and phone:
            score += 20
            breakdown.append("Complete Contact (Email + Phone): +20 pts")
        elif email:
            score += 10
            breakdown.append("Email Only: +10 pts")

        # Factor 3: Lead Source Intent
        if lead_source in ["Direct Demo Request", "Inbound Webhook"]:
            score += 25
            breakdown.append("High Intent Channel: +25 pts")
        elif lead_source == "Organic Search":
            score += 15
            breakdown.append("Inbound Organic: +15 pts")
        else:
            score += 5
            breakdown.append("Standard Channel: +5 pts")

        # Factor 4: Corporate Domain Legitimacy
        free_domains = ["@gmail.", "@yahoo.", "@hotmail.", "@outlook.", "@icloud."]
        if not any(dom in email for dom in free_domains):
            score += 15
            breakdown.append("Verified Corporate Email Domain: +15 pts")

        # Classification
        if score >= 75:
            classification = "Hot (High Priority)"
            status = "Sales Qualified (SQL)"
        elif score >= 50:
            classification = "Warm (Nurture)"
            status = "Marketing Qualified (MQL)"
        else:
            classification = "Cold"
            status = "Unqualified Lead"

        if existing_lead:
            logs.append(f"[DELUGE::INFO] Duplicate Lead matched with ID: {existing_lead.id}. Updating record.")
            existing_lead.company = company
            if phone:
                existing_lead.phone = phone
            existing_lead.annual_revenue = annual_revenue
            existing_lead.lead_score = score
            existing_lead.lead_classification = classification
            existing_lead.lead_status = status
            existing_lead.score_breakdown = breakdown
            target_lead = existing_lead
        else:
            new_id = db.next_lead_id()
            rep_idx = new_id % len(SALES_REPRESENTATIVES)
            assigned_rep = SALES_REPRESENTATIVES[rep_idx]["name"]

            logs.append(f"[DELUGE::INFO] Creating new Zoho CRM Lead with ID: {new_id}")
            logs.append(f"[DELUGE::INFO] Round-robin assigned to: {assigned_rep}")

            target_lead = Lead(
                id=new_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                annual_revenue=annual_revenue,
                lead_source=lead_source,
                lead_score=score,
                lead_classification=classification,
                lead_status=status,
                assigned_rep=assigned_rep,
                score_breakdown=breakdown
            )
            db.leads[new_id] = target_lead

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        telemetry = {
            "execution_time_ms": elapsed_ms,
            "statements_evaluated": 42,
            "logs": logs,
            "deluge_version": "Deluge 2.0 (Zoho Cloud Engine)",
            "status": "COMPLETED_SUCCESS"
        }

        # Trigger outbound webhook notification
        DelugeEngine.dispatch_webhook(
            event_type="lead.scored_and_assigned",
            payload={
                "lead_id": target_lead.id,
                "name": f"{target_lead.first_name} {target_lead.last_name}",
                "company": target_lead.company,
                "score": target_lead.lead_score,
                "classification": target_lead.lead_classification,
                "assigned_rep": target_lead.assigned_rep
            }
        )

        return target_lead, telemetry

    @staticmethod
    def execute_lead_conversion_to_deal(lead_id: int, deal_amount: float = 24000.0) -> Tuple[Deal, Dict[str, Any]]:
        """
        Executes script:
        - 3_deal_conversion_workflow.dg
        """
        start_time = time.time()
        logs = []

        lead = db.leads.get(lead_id)
        if not lead:
            raise ValueError(f"Lead ID {lead_id} not found in CRM.")

        logs.append(f"[DELUGE::INFO] Converting Lead #{lead_id} ({lead.first_name} {lead.last_name}) to Opportunity/Deal.")
        logs.append(f"[DELUGE::INFO] Creating Account '{lead.company}' in Zoho CRM.")
        logs.append(f"[DELUGE::INFO] Creating Contact '{lead.first_name} {lead.last_name}' linked to Account.")

        deal_id = db.next_deal_id()
        closing_date = (date.today() + timedelta(days=25)).isoformat()
        deal_name = f"{lead.company} - ZohoPulse SaaS License"

        new_deal = Deal(
            id=deal_id,
            deal_name=deal_name,
            account_name=lead.company,
            contact_name=f"{lead.first_name} {lead.last_name}",
            amount=deal_amount,
            stage="Proposal / Value Proposition",
            probability=50,
            closing_date=closing_date,
            owner=lead.assigned_rep,
            lead_id=lead.id
        )
        db.deals[deal_id] = new_deal

        lead.lead_status = "Converted to Deal"
        logs.append(f"[DELUGE::INFO] Deal #{deal_id} created with initial stage 'Proposal / Value Proposition'.")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        telemetry = {
            "execution_time_ms": elapsed_ms,
            "statements_evaluated": 28,
            "logs": logs,
            "deal_id": deal_id,
            "status": "CONVERTED_SUCCESS"
        }

        DelugeEngine.dispatch_webhook(
            event_type="deal.created_from_lead",
            payload={"deal_id": deal_id, "deal_name": deal_name, "amount": deal_amount, "owner": lead.assigned_rep}
        )

        return new_deal, telemetry

    @staticmethod
    def execute_deal_closed_won_to_invoice(deal_id: int) -> Tuple[Invoice, Dict[str, Any]]:
        """
        Executes script:
        - 4_auto_invoice_generator_books.dg
        """
        start_time = time.time()
        logs = []

        deal = db.deals.get(deal_id)
        if not deal:
            raise ValueError(f"Deal ID {deal_id} not found.")

        deal.stage = "Closed Won"
        deal.probability = 100
        logs.append(f"[DELUGE::INFO] Deal #{deal_id} stage progressed to 'Closed Won'. Probability set to 100%.")

        invoice_id = db.next_invoice_id()
        invoice_num = f"INV-2026-{invoice_id:04d}"
        deal.invoice_id = f"ZBOOKS-{invoice_id}"
        deal.invoice_number = invoice_num

        logs.append(f"[DELUGE::INFO] Invoking Zoho Books API task: zoho.books.createRecord('Invoices', orgId, invoiceMap)")

        # Create itemized invoice
        line_item_sub = InvoiceLineItem(
            name=deal.deal_name,
            description="Annual SaaS Platform Enterprise License & SLA Support",
            rate=round(deal.amount * 0.85, 2),
            quantity=1,
            amount=round(deal.amount * 0.85, 2)
        )
        line_item_onboard = InvoiceLineItem(
            name="Implementation & Deployment Setup",
            description="Dedicated Integration Architect & SSO/CRM Provisioning",
            rate=round(deal.amount * 0.15, 2),
            quantity=1,
            amount=round(deal.amount * 0.15, 2)
        )

        subtotal = round(deal.amount, 2)
        tax = round(subtotal * 0.16, 2)  # Standard 16% corporate sales tax
        total = round(subtotal + tax, 2)

        new_invoice = Invoice(
            id=invoice_id,
            invoice_number=invoice_num,
            deal_id=deal.id,
            customer_name=deal.account_name,
            date=date.today().isoformat(),
            due_date=(date.today() + timedelta(days=15)).isoformat(),
            line_items=[line_item_sub, line_item_onboard],
            subtotal=subtotal,
            tax_amount=tax,
            total=total,
            status="Sent"
        )
        db.invoices[invoice_id] = new_invoice

        logs.append(f"[DELUGE::INFO] Invoice #{invoice_num} generated in Zoho Books. Total: ${total:,.2f}")
        logs.append(f"[DELUGE::INFO] Dispatched PDF invoice notification to customer billing address.")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        telemetry = {
            "execution_time_ms": elapsed_ms,
            "statements_evaluated": 54,
            "logs": logs,
            "invoice_number": invoice_num,
            "total_amount": total,
            "status": "INVOICE_GENERATED"
        }

        DelugeEngine.dispatch_webhook(
            event_type="invoice.generated_and_sent",
            payload={"invoice_id": invoice_id, "invoice_number": invoice_num, "deal_id": deal.id, "total": total}
        )

        return new_invoice, telemetry

    @staticmethod
    def dispatch_webhook(event_type: str, payload: Dict[str, Any]) -> WebhookLog:
        """
        Executes script:
        - 5_webhook_notification_dispatcher.dg
        """
        dest_url = "https://api.zohopulse.io/v1/webhooks/crm-events"
        signature = hashlib.sha256(f"{event_type}_{str(payload)}_secret".encode()).hexdigest()[:32]
        
        log = WebhookLog(
            id=db.next_log_id(),
            event_type=event_type,
            source="Zoho CRM Deluge Engine",
            destination=dest_url,
            payload=payload,
            status="delivered (HTTP 200)",
            signature=f"sha256={signature}",
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        db.webhook_logs.insert(0, log)
        if len(db.webhook_logs) > 50:
            db.webhook_logs.pop()
        return log
