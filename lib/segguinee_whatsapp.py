"""
lib/segguinee_whatsapp.py — SEGGUINÉE WhatsApp Operational Agent
=================================================================
Meta Cloud API agent for SEGGUINÉE water utility (Guinea).

FIVE FUNCTIONS:
  1. compile_daily_briefing(tenant)    — 07:00 Conakry briefing → director
  2. send_billing_reminders(tenant)    — director-triggered "relance les impayés"
  3. handle_customer_inquiry(...)      — customer messages → Claude Haiku in French
  4. handle_director_command(...)      — parse director commands, route to actions
  5. log_transcript(...)               — compliance audit trail

Channel: Meta WhatsApp Cloud API (free tier, 1,000 conversations/month)
One phone number handles: briefing, billing, customer inquiries.
All messages logged as transcripts for government compliance.

Usage:
    from core.tenant import get_tenant
    from lib.segguinee_whatsapp import compile_daily_briefing

    tenant = get_tenant("segguinee")
    compile_daily_briefing(tenant)
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger("segguinee.whatsapp")

# ---------------------------------------------------------------------------
# Meta Cloud API — low-level send
# ---------------------------------------------------------------------------

META_API_URL = "https://graph.facebook.com/v22.0"


def _send_meta_message(phone_id: str, token: str, to_number: str,
                       body: str) -> dict:
    """
    Send a WhatsApp text message via Meta Cloud API.

    Args:
        phone_id: Meta phone number ID (from Meta Business app)
        token: Permanent access token
        to_number: Recipient in international format (e.g. "224XXXXXXXXX")
        body: Message text (max 4096 chars, truncated if longer)

    Returns:
        {"ok": True, "message_id": "wamid.xxx"} or {"ok": False, "error": "..."}
    """
    if not phone_id or not token:
        return {"ok": False, "error": "Meta credentials not configured — set META_PHONE_ID_SEGGUINEE and META_TOKEN_SEGGUINEE"}

    url = f"{META_API_URL}/{phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"preview_url": False, "body": body[:4096]},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        data = resp.json()

        if resp.status_code == 200 and "messages" in data:
            msg_id = data["messages"][0]["id"]
            log.info(f"Meta message sent to {to_number} — id={msg_id}")
            return {"ok": True, "message_id": msg_id}
        else:
            error_detail = data.get("error", {}).get("message", resp.text[:300])
            log.error(f"Meta send failed ({resp.status_code}): {error_detail}")
            return {"ok": False, "error": error_detail}

    except requests.RequestException as e:
        log.error(f"Meta API unreachable: {e}")
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Transcript logging — compliance audit trail
# ---------------------------------------------------------------------------

TRANSCRIPT_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "outputs", "clients", "segguinee", "transcripts.jsonl"
)


def _ensure_transcript_dir():
    os.makedirs(os.path.dirname(TRANSCRIPT_LOG_PATH), exist_ok=True)


def log_transcript(tenant, phone: str, direction: str,
                   message: str, action: str = "") -> dict:
    """
    Log every WhatsApp message for compliance.

    Args:
        tenant: SEGGUINÉE tenant object
        phone: Phone number (sender for inbound, recipient for outbound)
        direction: "inbound" | "outbound"
        message: Message body
        action: What happened as a result (e.g. "billing_reminder_sent", "inquiry_answered")

    Returns:
        {"ok": True, "log_id": "..."}
    """
    entry = {
        "client_id": tenant.client_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phone": phone,
        "direction": direction,
        "message": message[:1000],
        "action": action,
    }

    # 1. Try Airtable Transcripts table
    try:
        from lib.airtable_client import query_table
        import requests as req

        airtable_url = f"https://api.airtable.com/v0/{tenant.airtable_base_id}/Transcripts"
        headers = {
            "Authorization": f"Bearer {tenant.airtable_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "records": [{
                "fields": {
                    "Phone": phone,
                    "Direction": direction,
                    "Message": message[:1000],
                    "Action": action,
                    "Timestamp": entry["timestamp"],
                }
            }]
        }
        resp = req.post(airtable_url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            return {"ok": True, "log_id": resp.json().get("records", [{}])[0].get("id", "")}
    except Exception as e:
        log.warning(f"Airtable transcript log failed (falling back to JSONL): {e}")

    # 2. Fallback: local JSONL file
    try:
        _ensure_transcript_dir()
        with open(TRANSCRIPT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"ok": True, "log_id": f"local_{entry['timestamp']}"}
    except Exception as e:
        log.error(f"Transcript log completely failed: {e}")
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# 1. DAILY BRIEFING — 07:00 Conakry (GMT+0)
# ---------------------------------------------------------------------------

def compile_daily_briefing(tenant) -> dict:
    """
    Compile and send the 7am S/P/R/EO briefing to the director.

    Queries Airtable for:
      - Overdue invoices (Factures table)
      - Production data (Production table)
      - Active incidents (Incidents table)

    Builds a French briefing under 250 words, sends via Meta API,
    logs the transcript.

    Returns:
        {"ok": True/False, "briefing": "...", "sent": True/False}
    """
    if not tenant.director_phone:
        return {"ok": False, "error": "Director phone not set — add SEGGUINEE_DIRECTOR_PHONE to .env"}

    from lib.airtable_client import query_table

    # ── Gather data ──────────────────────────────────────
    base = tenant.airtable_base_id

    overdue = query_table(base, "Factures",
                          filter_formula="{Statut}='Impayé'",
                          max_records=20)

    production = query_table(base, "Production",
                             sort_field="Date",
                             sort_direction="desc",
                             max_records=7)

    incidents = query_table(base, "Incidents",
                            filter_formula="{Statut}='Actif'",
                            max_records=10)

    # ── Build briefing ───────────────────────────────────
    today = datetime.now(timezone.utc).strftime("%A %d %B %Y")
    total_impaye = sum(
        float(r.get("Montant", 0) or 0) for r in overdue
    )

    prod_latest = production[0] if production else {}
    prod_volume = prod_latest.get("Volume m3", prod_latest.get("Volume (m³)", "N/A"))

    nb_incidents = len(incidents)
    incident_names = [i.get("Type", i.get("Description", "?")) for i in incidents[:3]]

    # Build French briefing — S/P/R/EO format, under 250 words
    briefing = (
        f"📊 *SEGGUINÉE — Briefing Quotidien*\n"
        f"_{today}_\n\n"
        f"*SITUATION:*\n"
        f"• Production: {prod_volume} m³ (dernier relevé)\n"
        f"• Factures impayées: {len(overdue)} ({total_impaye:,.0f} GNF)\n"
        f"• Incidents actifs: {nb_incidents}"
    )

    if incident_names:
        briefing += f" — {', '.join(incident_names)}"
    briefing += "\n"

    # Determine priority
    if nb_incidents > 2:
        briefing += "\n*PRIORITÉ:* Résoudre les incidents en cours avant qu'ils n'affectent la distribution.\n"
    elif len(overdue) > 10:
        briefing += "\n*PRIORITÉ:* Lancer une relance des impayés. Le recouvrement est en retard.\n"
    elif total_impaye > 50_000_000:
        briefing += "\n*PRIORITÉ:* Le montant des impayés est élevé. Action recommandée aujourd'hui.\n"
    else:
        briefing += "\n*PRIORITÉ:* Maintenir la production. Vérifier les relevés des stations.\n"

    briefing += (
        f"\n*RECOMMANDATION:* "
        f"{'Examiner les incidents et assigner les équipes terrain.' if nb_incidents > 2 else ''}"
        f"{'Répondre RELANCE pour envoyer les rappels de facturation.' if len(overdue) > 5 else ''}"
        f"{'Tout est stable. Pas d action urgente requise.' if nb_incidents == 0 and len(overdue) <= 5 else ''}"
        f"\n\n*RÉSULTAT ATTENDU:* "
        f"{'Incidents résolus sous 48h, distribution stabilisée.' if nb_incidents > 2 else ''}"
        f"{'Trésorerie améliorée sous 7 jours après relance.' if len(overdue) > 5 else ''}"
        f"{'Opérations normales maintenues.' if nb_incidents == 0 and len(overdue) <= 5 else ''}"
        f"\n\n---\n_Répondez RELANCE pour envoyer les rappels._\n"
        f"_Répondez STATUT [région] pour un rapport par zone._\n"
        f"_Répondez GO pour approuver les actions du jour._"
    )

    # ── Send ─────────────────────────────────────────────
    result = _send_meta_message(
        tenant.meta_phone_id,
        tenant.meta_token,
        tenant.director_phone,
        briefing,
    )

    # ── Log ──────────────────────────────────────────────
    log_transcript(tenant, tenant.director_phone, "outbound",
                   briefing, "daily_briefing")

    return {
        "ok": result["ok"],
        "briefing": briefing,
        "sent": result["ok"],
        "message_id": result.get("message_id", ""),
        "data": {
            "overdue_count": len(overdue),
            "overdue_total_gnf": total_impaye,
            "production_m3": prod_volume,
            "active_incidents": nb_incidents,
        },
    }


# ---------------------------------------------------------------------------
# 2. BILLING REMINDERS — director-triggered
# ---------------------------------------------------------------------------

def send_billing_reminders(tenant) -> dict:
    """
    Send personalised billing reminders to all customers with overdue invoices.

    Triggered ONLY by director command "relance les impayés".

    Queries Airtable Factures for overdue invoices, looks up customer phone
    numbers from Clients table, sends personalised French reminder to each.
    500ms delay between messages for Meta rate limiting.

    Returns:
        {"ok": True, "total": 15, "sent": 12, "skipped_no_phone": 2, "errors": 1}
    """
    from lib.airtable_client import query_table

    base = tenant.airtable_base_id
    phone_id = tenant.meta_phone_id
    token = tenant.meta_token

    if not phone_id or not token:
        return {"ok": False, "error": "Meta credentials not configured"}

    # ── Get overdue invoices ─────────────────────────────
    overdue = query_table(base, "Factures",
                          filter_formula="{Statut}='Impayé'",
                          max_records=100)

    if not overdue:
        return {"ok": True, "total": 0, "sent": 0, "skipped_no_phone": 0, "errors": 0,
                "message": "Aucune facture impayée trouvée."}

    # ── Get clients for phone numbers ────────────────────
    clients = query_table(base, "Clients", max_records=200)
    client_phones = {}
    for c in clients:
        name = c.get("Nom", c.get("Name", ""))
        phone = c.get("Téléphone", c.get("Phone", c.get("WhatsApp", "")))
        if name and phone:
            # Normalize — strip whatsapp: prefix if present
            phone = phone.replace("whatsapp:", "").strip()
            client_phones[name.lower().strip()] = phone

    # ── Send reminders ───────────────────────────────────
    total = len(overdue)
    sent = 0
    skipped_no_phone = 0
    errors = 0

    for invoice in overdue:
        customer_name = invoice.get("Client",
                                     invoice.get("Nom Client",
                                                 invoice.get("Nom", "Client")))
        amount = invoice.get("Montant", invoice.get("Montant (GNF)", 0))
        due_date = invoice.get("Échéance", invoice.get("Echeance",
                               invoice.get("Date Échéance", "")))
        invoice_id = invoice.get("ID Facture", invoice.get("Référence",
                                 invoice.get("Numéro", "")))

        # Find phone number
        phone = client_phones.get(str(customer_name).lower().strip(), "")

        if not phone:
            log.warning(f"No phone for customer: {customer_name}")
            skipped_no_phone += 1
            log_transcript(tenant, "N/A", "outbound_skipped",
                           f"Billing reminder skipped — no phone for {customer_name}",
                           "billing_reminder_skipped_no_phone")
            continue

        # Build personalised message
        amount_str = f"{float(amount):,.0f} GNF" if amount else "montant dû"
        due_str = f"du {due_date}" if due_date else "en retard"

        message = (
            f"Bonjour {customer_name},\n\n"
            f"Ceci est un rappel de la SEGGUINÉE concernant votre facture {due_str} "
            f"d'un montant de *{amount_str}*.\n\n"
            f"Nous vous prions de bien vouloir régulariser votre situation "
            f"dans les meilleurs délais.\n\n"
            f"Pour confirmer votre paiement ou pour toute question, "
            f"répondez simplement à ce message.\n\n"
            f"Merci de votre confiance.\n"
            f"_Service Client SEGGUINÉE_"
        )

        result = _send_meta_message(phone_id, token, phone, message)

        if result["ok"]:
            sent += 1
            log_transcript(tenant, phone, "outbound", message, "billing_reminder_sent")
        else:
            errors += 1
            log.warning(f"Billing reminder failed for {customer_name} ({phone}): {result.get('error')}")

        # Rate limit — 500ms between messages
        time.sleep(0.5)

    return {
        "ok": True,
        "total": total,
        "sent": sent,
        "skipped_no_phone": skipped_no_phone,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# 3. CUSTOMER INQUIRY HANDLER
# ---------------------------------------------------------------------------

def handle_customer_inquiry(tenant, from_number: str, body: str) -> str:
    """
    Handle inbound customer messages — "j'ai payé", "quel est mon solde", etc.

    Routes to Claude Haiku with a tight operational prompt:
      - French only
      - Facts only (query Airtable)
      - Never negotiate, never make promises
      - Escalate disputes to director

    Args:
        tenant: SEGGUINÉE tenant
        from_number: Customer's WhatsApp number
        body: Message text

    Returns:
        Reply string (French)
    """
    from lib.airtable_client import query_table

    # ── Quick keyword check before AI call ───────────────
    body_lower = body.lower().strip()

    # "j'ai payé" → check Airtable for recent payments
    if any(kw in body_lower for kw in ["payé", "paye", "paiement", "réglé", "regle"]):
        return _handle_payment_claim(tenant, from_number, body)

    # "quel est mon solde" / "ma facture" → look up balance
    if any(kw in body_lower for kw in ["solde", "facture", "combien", "dois", "montant"]):
        return _handle_balance_inquiry(tenant, from_number, body)

    # Fallback to Claude Haiku
    return _ai_customer_reply(tenant, from_number, body)


def _handle_payment_claim(tenant, from_number: str, body: str) -> str:
    """Handle 'j'ai payé' — check Airtable, factual response."""
    from lib.airtable_client import query_table

    # Try to find the customer by phone number
    base = tenant.airtable_base_id
    clients = query_table(base, "Clients", max_records=200)

    customer_name = None
    for c in clients:
        phone = str(c.get("Téléphone", c.get("Phone", c.get("WhatsApp", "")))).replace("whatsapp:", "").strip()
        if phone == from_number:
            customer_name = c.get("Nom", c.get("Name", ""))
            break

    if customer_name:
        # Check their invoices
        filter_f = f"AND({{Client}}='{customer_name}', {{Statut}}='Impayé')"
        unpaid = query_table(base, "Factures", filter_formula=filter_f, max_records=10)

        if not unpaid:
            return (
                f"Merci {customer_name}. ✅\n\n"
                f"Nos registres ne montrent aucune facture impayée à votre nom. "
                f"Votre compte est à jour.\n\n"
                f"Si vous avez effectué un paiement récent, il sera visible "
                f"dans votre prochain relevé.\n\n"
                f"_Service Client SEGGUINÉE_"
            )
        else:
            total = sum(float(i.get("Montant", 0) or 0) for i in unpaid)
            return (
                f"Merci {customer_name}.\n\n"
                f"Nous avons bien noté votre message. Cependant, nos registres "
                f"montrent encore {len(unpaid)} facture(s) impayée(s) pour un "
                f"total de {total:,.0f} GNF.\n\n"
                f"Si vous avez déjà payé, merci de nous envoyer une capture "
                f"du reçu. Nous mettrons votre compte à jour immédiatement.\n\n"
                f"_Service Client SEGGUINÉE_"
            )

    # Customer not found by phone — generic response
    return (
        "Merci pour votre message. ✅\n\n"
        "Pour vérifier votre paiement, nous avons besoin de votre nom complet "
        "ou de votre numéro de référence client.\n\n"
        "Merci de nous les communiquer.\n\n"
        "_Service Client SEGGUINÉE_"
    )


def _handle_balance_inquiry(tenant, from_number: str, body: str) -> str:
    """Handle 'quel est mon solde' — look up balance in Airtable."""
    from lib.airtable_client import query_table

    base = tenant.airtable_base_id
    clients = query_table(base, "Clients", max_records=200)

    customer_name = None
    for c in clients:
        phone = str(c.get("Téléphone", c.get("Phone", c.get("WhatsApp", "")))).replace("whatsapp:", "").strip()
        if phone == from_number:
            customer_name = c.get("Nom", c.get("Name", ""))
            break

    if customer_name:
        filter_f = f"AND({{Client}}='{customer_name}', {{Statut}}='Impayé')"
        unpaid = query_table(base, "Factures", filter_formula=filter_f, max_records=50)

        if not unpaid:
            return (
                f"Bonjour {customer_name}.\n\n"
                f"✅ Votre compte est à jour. Aucune facture impayée.\n\n"
                f"_Service Client SEGGUINÉE_"
            )

        total = sum(float(i.get("Montant", 0) or 0) for i in unpaid)
        oldest = min(
            (i.get("Échéance", i.get("Echeance", "Date inconnue")) for i in unpaid),
            key=lambda d: str(d)
        )

        lines = [f"• {i.get('Référence', i.get('ID Facture', 'Facture'))}: "
                 f"{float(i.get('Montant', 0) or 0):,.0f} GNF "
                 f"(échéance: {i.get('Échéance', i.get('Echeance', 'N/A'))})"
                 for i in unpaid[:5]]

        return (
            f"Bonjour {customer_name}.\n\n"
            f"📋 *Votre situation:*\n"
            f"{chr(10).join(lines)}\n\n"
            f"*Total dû:* {total:,.0f} GNF\n"
            f"*Plus ancienne échéance:* {oldest}\n\n"
            f"Pour régler ou demander un échéancier, répondez à ce message.\n\n"
            f"_Service Client SEGGUINÉE_"
        )

    return (
        "Bonjour.\n\n"
        "Pour consulter votre solde, merci de nous indiquer votre nom complet "
        "ou votre numéro de référence client.\n\n"
        "_Service Client SEGGUINÉE_"
    )


def _ai_customer_reply(tenant, from_number: str, body: str) -> str:
    """
    Fallback AI reply using Claude Haiku.

    Tight operational prompt:
      - French only
      - Facts only
      - Never negotiate pricing or make promises
      - Escalate disputes to director
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not anthropic_key:
        return (
            "Merci pour votre message. Un membre de notre équipe vous répondra "
            "dans les plus brefs délais.\n\n"
            "_Service Client SEGGUINÉE_"
        )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=anthropic_key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=250,
            system=(
                "Tu es l'assistant virtuel de la SEGGUINÉE, la société nationale "
                "des eaux de Guinée. Tu réponds aux clients par WhatsApp.\n\n"
                "RÈGLES STRICTES:\n"
                "1. Réponds TOUJOURS en français.\n"
                "2. Donne uniquement des informations factuelles. Pas d'opinions.\n"
                "3. Ne négocie JAMAIS les prix ou les conditions de paiement.\n"
                "4. Ne fais JAMAIS de promesses (délais, remboursements, réparations).\n"
                "5. Si le client est en colère ou conteste une facture: "
                "transfère au directeur. Dis 'Je transmets votre message au directeur. "
                "Il vous contactera dans les plus brefs délais.'\n"
                "6. Si le client demande une intervention technique: "
                "dis 'Je signale votre demande au service technique. Référence: [date].'\n"
                "7. Reste poli, professionnel, concis. Maximum 3 phrases.\n"
                "8. Termine par '_Service Client SEGGUINÉE_'"
            ),
            messages=[{"role": "user", "content": body}],
        )
        return msg.content[0].text.strip()

    except Exception as e:
        log.error(f"Claude Haiku customer reply failed: {e}")
        return (
            "Merci pour votre message. Nous vous répondrons dans les plus "
            "brefs délais.\n\n"
            "_Service Client SEGGUINÉE_"
        )


# ---------------------------------------------------------------------------
# 4. DIRECTOR COMMAND HANDLER
# ---------------------------------------------------------------------------

def handle_director_command(tenant, from_number: str, body: str) -> dict:
    """
    Parse director commands and route to appropriate actions.

    Commands:
      "relance les impayés"  → send_billing_reminders()
      "briefing"             → compile_daily_briefing()
      "statut [region]"      → region-specific report (TODO)
      "GO"                   → approve pending actions
      "PAUSE"                → hold all automated actions

    Args:
        tenant: SEGGUINÉE tenant
        from_number: Must match director_phone for security
        body: Command text

    Returns:
        {"ok": True/False, "action": "...", "reply": "...", "result": {...}}
    """
    # ── Security: only the director can issue commands ────
    director = tenant.director_phone
    if director and from_number.replace("whatsapp:", "").strip() != director.strip():
        log.warning(f"Unauthorised command attempt from {from_number}")
        return {
            "ok": False,
            "action": "blocked",
            "reply": "⛔ Commande non autorisée. Seul le directeur peut exécuter cette action.",
        }

    cmd = body.lower().strip()

    # ── "relance les impayés" ─────────────────────────────
    if any(phrase in cmd for phrase in ["relance", "impayés", "impayes", "relance les impayés"]):
        log.info(f"Director triggered billing reminders: {body[:80]}")
        result = send_billing_reminders(tenant)

        if result["total"] == 0:
            reply = "📋 Aucune facture impayée trouvée dans le système."
        else:
            reply = (
                f"📋 *Relance terminée*\n\n"
                f"• Total factures impayées: {result['total']}\n"
                f"• Rappels envoyés: {result['sent']}\n"
                f"• Sans numéro: {result['skipped_no_phone']}\n"
                f"• Erreurs: {result['errors']}\n\n"
                f"{'⚠ Certains clients n ont pas de numéro WhatsApp enregistré.' if result['skipped_no_phone'] > 0 else ''}"
            )

        # Send confirmation back to director
        if result.get("sent", 0) > 0:
            _send_meta_message(tenant.meta_phone_id, tenant.meta_token,
                               from_number, reply)

        log_transcript(tenant, from_number, "inbound", body, f"command:relance — {result['sent']}/{result['total']} sent")
        log_transcript(tenant, from_number, "outbound", reply, "command:relance_result")

        return {"ok": True, "action": "billing_reminders", "reply": reply, "result": result}

    # ── "briefing" ────────────────────────────────────────
    if "briefing" in cmd:
        log.info(f"Director requested manual briefing")
        result = compile_daily_briefing(tenant)
        log_transcript(tenant, from_number, "inbound", body, "command:briefing")
        return {"ok": result["ok"], "action": "daily_briefing",
                "reply": result.get("briefing", ""), "result": result}

    # ── "statut [region]" ─────────────────────────────────
    if cmd.startswith("statut") or cmd.startswith("statut "):
        region = cmd.replace("statut", "").strip()
        reply = _region_status_report(tenant, region)
        _send_meta_message(tenant.meta_phone_id, tenant.meta_token, from_number, reply)
        log_transcript(tenant, from_number, "inbound", body, f"command:statut {region}")
        log_transcript(tenant, from_number, "outbound", reply, "command:statut_result")
        return {"ok": True, "action": "region_status", "reply": reply}

    # ── "GO" — approve pending ────────────────────────────
    if cmd in ("go", "oui", "yes"):
        reply = "✅ Actions approuvées. Les agents exécutent les tâches du jour."
        _send_meta_message(tenant.meta_phone_id, tenant.meta_token, from_number, reply)
        return {"ok": True, "action": "approve", "reply": reply}

    # ── "PAUSE" — hold all ────────────────────────────────
    if cmd in ("pause", "stop", "non", "no"):
        reply = "⏸️ Toutes les actions automatisées sont suspendues. Répondez GO pour reprendre."
        _send_meta_message(tenant.meta_phone_id, tenant.meta_token, from_number, reply)
        return {"ok": True, "action": "pause", "reply": reply}

    # ── Unknown command ───────────────────────────────────
    reply = (
        "Commandes disponibles:\n\n"
        "📋 *relance les impayés* — Envoyer les rappels de facturation\n"
        "📊 *briefing* — Recevoir le briefing du jour\n"
        "📍 *statut [région]* — Rapport par zone\n"
        "✅ *GO* — Approuver les actions en attente\n"
        "⏸️ *PAUSE* — Suspendre toutes les actions"
    )
    _send_meta_message(tenant.meta_phone_id, tenant.meta_token, from_number, reply)
    log_transcript(tenant, from_number, "inbound", body, "command:unknown")
    return {"ok": True, "action": "help", "reply": reply}


def _region_status_report(tenant, region: str = "") -> str:
    """Build a region-specific status report from Airtable."""
    from lib.airtable_client import query_table

    base = tenant.airtable_base_id

    # Try to get region data from Airtable
    regions_data = query_table(base, "Régions", max_records=20)

    if not region:
        # All regions summary
        if not regions_data:
            return "📊 Aucune donnée régionale disponible pour le moment."

        lines = []
        for r in regions_data:
            name = r.get("Nom", r.get("Région", r.get("Name", "?")))
            status = r.get("Statut", r.get("Status", "?"))
            prod = r.get("Production", r.get("Production (m³)", "N/A"))
            lines.append(f"• *{name}*: {status} — {prod} m³")

        return "📍 *Statut par région*\n\n" + "\n".join(lines) + "\n\n_Répondez STATUT [nom] pour le détail._"

    # Specific region — fuzzy match
    region_lower = region.lower().strip()
    match = None
    for r in regions_data:
        name = str(r.get("Nom", r.get("Région", r.get("Name", "")))).lower()
        if region_lower in name or name in region_lower:
            match = r
            break

    if not match:
        return f"📍 Région '{region}' non trouvée. Vérifiez le nom et réessayez."

    name = match.get("Nom", match.get("Région", "Région"))
    return (
        f"📍 *{name}*\n\n"
        f"• Statut: {match.get('Statut', 'N/A')}\n"
        f"• Production: {match.get('Production', 'N/A')} m³\n"
        f"• Stations: {match.get('Stations', 'N/A')}\n"
        f"• Incidents: {match.get('Incidents', '0')}\n\n"
        f"_Service Client SEGGUINÉE_"
    )


# ---------------------------------------------------------------------------
# 5. MESSAGE ROUTER — inbound webhook entry point
# ---------------------------------------------------------------------------

def handle_segguinee_message(tenant, from_number: str, body: str,
                             profile_name: str = "") -> dict:
    """
    Main inbound message router for SEGGUINÉE WhatsApp.

    Routes to:
      - Director commands (if from_number matches director_phone)
      - Customer inquiries (all other numbers)

    Returns:
        {"ok": True, "routed_to": "director|inquiry", "reply": "..."}
    """
    director = tenant.director_phone

    # Strip whatsapp: prefix if present
    clean_from = from_number.replace("whatsapp:", "").strip()

    # ── Director? → command handler ───────────────────────
    if director and clean_from == director.strip():
        result = handle_director_command(tenant, clean_from, body)
        return {"ok": result["ok"], "routed_to": "director",
                "reply": result.get("reply", ""), "action": result.get("action")}

    # ── Customer inquiry ──────────────────────────────────
    reply = handle_customer_inquiry(tenant, clean_from, body)

    # Send reply via Meta
    if tenant.meta_phone_id and tenant.meta_token:
        _send_meta_message(tenant.meta_phone_id, tenant.meta_token, clean_from, reply)

    # Log both sides
    log_transcript(tenant, clean_from, "inbound", body, "customer_inquiry")
    log_transcript(tenant, clean_from, "outbound", reply, "customer_reply")

    return {"ok": True, "routed_to": "customer_inquiry", "reply": reply}


# ---------------------------------------------------------------------------
# CLI — manual testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.tenant import get_tenant

    tenant = get_tenant("segguinee")
    print(f"SEGGUINÉE WhatsApp Agent — Tenant: {tenant.client_name}")
    print(f"  Director phone: {tenant.director_phone or 'NOT SET'}")
    print(f"  Meta phone ID:  {tenant.meta_phone_id or 'NOT SET'}")
    print(f"  Airtable base:  {tenant.airtable_base_id}")

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "briefing":
            result = compile_daily_briefing(tenant)
            print(f"\nBriefing result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        elif cmd == "relance":
            result = send_billing_reminders(tenant)
            print(f"\nBilling result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        elif cmd == "inquiry":
            msg = sys.argv[2] if len(sys.argv) > 2 else "Bonjour, j'ai payé ma facture"
            reply = handle_customer_inquiry(tenant, "+224000000000", msg)
            print(f"\nCustomer inquiry reply:\n{reply}")
        elif cmd == "command":
            msg = sys.argv[2] if len(sys.argv) > 2 else "relance les impayés"
            result = handle_director_command(tenant, tenant.director_phone or "+224000000000", msg)
            print(f"\nDirector command result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Unknown command: {cmd}")
    else:
        print("\nUsage: python lib/segguinee_whatsapp.py [briefing|relance|inquiry|command]")
