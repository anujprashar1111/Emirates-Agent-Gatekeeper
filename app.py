"""
Emirates Agent Gatekeeper - Web Application with Permanent CSV Audit Logging & Test Cases
Project: Emirates Agent Gatekeeper (College MBA Project)
Student Enrolment No: PGD202566060

Features:
- Enrolment Number PGD202566060 prominently displayed on the main screen.
- Gatekeeper Policy Engine enforcing Rules R1 through R8 across 4 actions:
  View fares, Book flight, Change flight, Refund.
- Agent Management:
  * Register new AI agents with customer name.
  * List all agents with ACTIVE / REVOKED status.
  * Revoke agents with exact date and time permanently saved in agents_registry.json.
  * Never allow revoked agents to make new requests.
- Permanent Audit Logging in audit_log.csv:
  * Every request is permanently appended with Date and Time, Customer Name, AI Agent Name,
    Requested Action, Amount in INR, Final Decision, Rule Number, and Reason.
  * Agent registration and revocation events are recorded with exact timestamps.
  * Never overwrites previous records; all history is preserved.
  * Dedicated interactive Audit Log dashboard table with search and filtering.
- Sample Test Cases Section:
  * Displays the six core sample test cases showing Expected vs. Actual decisions, rules, and match status.
"""

from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import streamlit as st

from gatekeeper import (
    evaluate_agent_request,
    AgentTrustStatus,
    GatekeeperDecision,
    VALID_ACTIONS,
    load_agents_registry,
    register_agent,
    revoke_agent,
    list_agents,
    get_default_registry_path,
)
from audit_logger import (
    log_audit_event,
    load_audit_log,
    get_default_audit_log_path,
    AUDIT_CSV_COLUMNS,
)
from sample_test_cases import SAMPLE_TEST_CASES, run_sample_test_cases

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Emirates Agent Gatekeeper | MBA Project (PGD202566060)",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling - Emirates Luxury Aesthetic
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #9E0D14 0%, #D71921 55%, #BA9B38 100%);
            padding: 22px 28px;
            border-radius: 12px;
            color: #FFFFFF;
            margin-bottom: 20px;
            box-shadow: 0 4px 18px rgba(215, 25, 33, 0.22);
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .hero-subtitle {
            font-size: 1.02rem;
            opacity: 0.94;
            margin-top: 5px;
            margin-bottom: 10px;
            font-weight: 400;
        }

        /* Prominent Academic Enrolment Badge */
        .enrolment-badge-main {
            display: inline-block;
            background: #FFFFFF;
            color: #A80D14;
            padding: 8px 18px;
            border-radius: 30px;
            font-weight: 800;
            font-size: 1.02rem;
            letter-spacing: 0.7px;
            border: 2px solid #BA9B38;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.18);
        }

        .enrolment-badge-sidebar {
            background: #FFF4F4;
            color: #D71921;
            border: 1.5px solid #D71921;
            border-radius: 8px;
            padding: 10px 14px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 16px;
            font-size: 0.95rem;
        }

        /* Cards & Metric Containers */
        .mgmt-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1E2229;
            border-bottom: 2px solid #D71921;
            padding-bottom: 6px;
            margin-bottom: 14px;
        }

        /* Decision Result Badges */
        .decision-allowed {
            background: #E8F8F0;
            border-left: 6px solid #10B981;
            border-radius: 8px;
            padding: 18px 22px;
            margin-top: 15px;
        }

        .decision-confirmation {
            background: #FFFBEB;
            border-left: 6px solid #F59E0B;
            border-radius: 8px;
            padding: 18px 22px;
            margin-top: 15px;
        }

        .decision-blocked {
            background: #FEF2F2;
            border-left: 6px solid #EF4444;
            border-radius: 8px;
            padding: 18px 22px;
            margin-top: 15px;
        }

        .revocation-stamp-box {
            background: #FEE2E2;
            border: 1px dashed #DC2626;
            border-radius: 6px;
            padding: 8px 12px;
            color: #991B1B;
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .rule-chip {
            display: inline-block;
            background: #1E2229;
            color: #FFFFFF;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.85rem;
            margin-bottom: 8px;
        }

        /* Disclaimer Footer */
        .disclaimer-banner {
            background: #FFF8E7;
            border: 1px dashed #C5A059;
            border-radius: 8px;
            padding: 12px 16px;
            color: #7A5812;
            font-size: 0.85rem;
            margin-top: 25px;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Initialize Session State
# -----------------------------------------------------------------------------
if "customer_name_input" not in st.session_state:
    st.session_state.customer_name_input = "Aarav Sharma"

if "agent_name_input" not in st.session_state:
    st.session_state.agent_name_input = "Emirates Concierge AI"

if "action_input" not in st.session_state:
    st.session_state.action_input = "Book flight"

if "amount_input" not in st.session_state:
    st.session_state.amount_input = 12500.0

if "spending_limit_input" not in st.session_state:
    st.session_state.spending_limit_input = 20000.0


# -----------------------------------------------------------------------------
# Sidebar: Academic Info & Quick Test Presets (R1 to R8)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="enrolment-badge-sidebar">
            🎓 <b>STUDENT PROJECT</b><br>
            Enrolment No: <b>PGD202566060</b><br>
            <span style="font-size:0.8rem; color:#6B7280;">MBA College Project</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚡ Quick Test Presets (R1 – R8)")
    st.caption("Click any preset to prefill and demonstrate the exact gatekeeper rules:")

    presets = [
        (
            "R1: Unknown Agent",
            {
                "customer": "Vikram Seth",
                "agent": "ShadowBot-Unknown-99",
                "action": "View fares",
                "amount": 0.0,
                "limit": 20000.0,
            },
        ),
        (
            "R2: Revoked Agent",
            {
                "customer": "Rohan Mehra",
                "agent": "Rogue AutoBooker v2",
                "action": "Book flight",
                "amount": 8000.0,
                "limit": 20000.0,
            },
        ),
        (
            "R3: View Fares (Active)",
            {
                "customer": "Ananya Roy",
                "agent": "Amadeus TravelBot",
                "action": "View fares",
                "amount": 0.0,
                "limit": 20000.0,
            },
        ),
        (
            "R4: Booking Within Limit",
            {
                "customer": "Priya Nair",
                "agent": "Emirates Concierge AI",
                "action": "Book flight",
                "amount": 14500.0,
                "limit": 20000.0,
            },
        ),
        (
            "R4: Booking Exceeds Limit",
            {
                "customer": "Karan Kapoor",
                "agent": "Emirates Concierge AI",
                "action": "Book flight",
                "amount": 18000.0,
                "limit": 10000.0,
            },
        ),
        (
            "R5: Booking > ₹20,000",
            {
                "customer": "Sameer Joshi",
                "agent": "Siri Travel Assistant",
                "action": "Book flight",
                "amount": 42000.0,
                "limit": 50000.0,
            },
        ),
        (
            "R6: Change Flight",
            {
                "customer": "Deepak Chopra",
                "agent": "Expedia Corporate Agent",
                "action": "Change flight",
                "amount": 3500.0,
                "limit": 20000.0,
            },
        ),
        (
            "R7: Refund Request",
            {
                "customer": "Sunita Rao",
                "agent": "Emirates Concierge AI",
                "action": "Refund",
                "amount": 28000.0,
                "limit": 20000.0,
            },
        ),
        (
            "R8: Invalid Request",
            {
                "customer": "",
                "agent": "Emirates Concierge AI",
                "action": "Book flight",
                "amount": -500.0,
                "limit": 20000.0,
            },
        ),
    ]

    for label, preset in presets:
        if st.button(label, use_container_width=True):
            st.session_state.customer_name_input = preset["customer"]
            st.session_state.agent_name_input = preset["agent"]
            st.session_state.action_input = preset["action"]
            st.session_state.amount_input = float(preset["amount"])
            st.session_state.spending_limit_input = float(preset["limit"])
            st.rerun()

    st.divider()

    # Storage indicators
    reg_path = get_default_registry_path()
    audit_path = get_default_audit_log_path()
    st.markdown("### 💾 Storage Status")
    st.caption(f"**Agents Registry:** `{reg_path.name}`\n\n**Audit Log:** `{audit_path.name}`")
    all_agents_current = list_agents()
    active_count = sum(1 for a in all_agents_current if a.get("status") == "ACTIVE")
    revoked_count = sum(1 for a in all_agents_current if a.get("status") == "REVOKED")
    st.markdown(f"• Active Agents: **{active_count}**\n• Revoked Agents: **{revoked_count}**")

    df_audit_quick = load_audit_log()
    st.markdown(f"• Permanent Audit Records: **{len(df_audit_quick)}**")


# -----------------------------------------------------------------------------
# Main Screen: Hero Banner with Prominent Enrolment Number
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="hero-title">
                    <span>✈️ Emirates Agent Gatekeeper</span>
                </div>
                <div class="hero-subtitle">
                    Autonomous Customer AI Agent Request Governance & Permanent CSV Audit Logging System
                </div>
            </div>
            <div>
                <div class="enrolment-badge-main">
                    STUDENT ENROLMENT NO: PGD202566060
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Top-Level Tabs: Gatekeeper, Agent Management, Test Cases, Audit Log, Rules Matrix
# -----------------------------------------------------------------------------
tab_gateway, tab_mgmt, tab_testcases, tab_audit, tab_rules = st.tabs(
    [
        "🛡️ Request Gatekeeper",
        "🤖 AI Agent Management",
        "🧪 Sample Test Cases (6 Scenarios)",
        "📊 Audit Log Dashboard",
        "📖 Policy Matrix (R1 – R8)",
    ]
)

# =============================================================================
# TAB 1: REQUEST GATEKEEPER (Core Evaluation Dashboard)
# =============================================================================
with tab_gateway:
    col_input, col_decision = st.columns([1.15, 1.0], gap="large")

    with col_input:
        st.markdown("#### 📝 Evaluate Incoming Agent Request")
        st.caption("Inspect and govern incoming requests submitted by customer autonomous AI agents.")

        # Robust Agent Picker: synchronizes without overwriting custom inputs
        registry_agents = list_agents()
        agent_names_list = [a["agent_name"] for a in registry_agents]
        quick_picker_options = ["Custom / Manual Input"] + agent_names_list

        current_selected_agent = st.session_state.get("agent_name_input", "")
        if current_selected_agent in agent_names_list:
            default_idx = quick_picker_options.index(current_selected_agent)
        else:
            default_idx = 0

        selected_picker = st.selectbox(
            "Select from Registered Agents (or choose Manual Input):",
            options=quick_picker_options,
            index=default_idx,
            help="Select an agent from the persistent registry to autofill, or choose Manual Input to test any agent.",
        )

        # Only update if the user switched to a specific registered agent
        if selected_picker != "Custom / Manual Input" and selected_picker != current_selected_agent:
            matched_agent = next((a for a in registry_agents if a["agent_name"] == selected_picker), None)
            if matched_agent:
                st.session_state.customer_name_input = matched_agent.get("customer_name", st.session_state.customer_name_input)
                st.session_state.agent_name_input = matched_agent.get("agent_name", st.session_state.agent_name_input)
                st.rerun()

        customer_name = st.text_input(
            "1. Customer Name",
            value=st.session_state.customer_name_input,
            placeholder="e.g. Aarav Sharma",
            help="Name of the customer whose account authorized the AI agent.",
        )

        agent_name = st.text_input(
            "2. AI Agent Name",
            value=st.session_state.agent_name_input,
            placeholder="e.g. Emirates Concierge AI, Amadeus TravelBot",
            help="Registered name/identifier of the AI agent submitting the request.",
        )

        col_act, col_amt = st.columns([1, 1])

        with col_act:
            action_index = (
                VALID_ACTIONS.index(st.session_state.action_input)
                if st.session_state.action_input in VALID_ACTIONS
                else 0
            )
            action = st.selectbox(
                "3. Action",
                options=VALID_ACTIONS,
                index=action_index,
                help="The action requested by the AI agent.",
            )

        with col_amt:
            is_view_fares = action == "View fares"
            amount_val = 0.0 if is_view_fares else float(st.session_state.amount_input)
            amount_inr = st.number_input(
                "4. Amount in INR (₹)",
                value=amount_val,
                min_value=-1000.0,
                max_value=1000000.0,
                step=500.0,
                format="%.2f",
                disabled=is_view_fares,
                help="Transaction value in INR. Disabled for read-only 'View fares'.",
            )

        spending_limit = st.number_input(
            "Customer-Authorised Spending Limit (₹)",
            value=float(st.session_state.spending_limit_input),
            min_value=0.0,
            max_value=500000.0,
            step=1000.0,
            format="%.2f",
            help="Maximum spending amount customer authorized for autonomous transactions (Rule R4).",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        check_button = st.button(
            "🔒 Check Request",
            type="primary",
            use_container_width=True,
        )

    with col_decision:
        st.markdown("#### ⚖️ Gatekeeper Policy Decision")
        st.caption("Live policy enforcement using Emirates security rules R1 to R8.")

        # Real-time evaluation against persistent JSON registry
        response = evaluate_agent_request(
            customer_name=customer_name,
            agent_name=agent_name,
            action=action,
            amount_inr=amount_inr,
            customer_spending_limit=spending_limit,
        )

        # When Check Request is clicked: permanently append to audit_log.csv
        if check_button:
            log_audit_event(
                customer_name=customer_name,
                agent_name=agent_name,
                action=action,
                amount_inr=amount_inr,
                final_decision=response.decision.value,
                rule_number=response.rule_number,
                reason=response.reason,
            )
            st.toast(f"✅ Request logged to audit_log.csv: {response.decision.value} ({response.rule_number})")

        # Visual Decision Cards
        if response.decision == GatekeeperDecision.ALLOWED:
            st.markdown(
                f"""
                <div class="decision-allowed">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="rule-chip">RULE {response.rule_number}</span>
                        <span style="color:#10B981; font-weight:800; font-size:1.15rem;">STATUS: PERMITTED</span>
                    </div>
                    <h2 style="color:#065F46; margin:6px 0 10px 0; font-size:1.75rem;">
                        ✅ ALLOWED
                    </h2>
                    <p style="color:#1F2937; font-size:0.98rem; line-height:1.5; margin-bottom:10px;">
                        <b>Policy Rationale:</b><br>{response.reason}
                    </p>
                    <div style="font-size:0.85rem; color:#047857;">
                        ✓ Request verified and dispatched directly to Emirates Reservation Core.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif response.decision == GatekeeperDecision.REQUIRES_CONFIRMATION:
            st.markdown(
                f"""
                <div class="decision-confirmation">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="rule-chip" style="background:#B45309;">RULE {response.rule_number}</span>
                        <span style="color:#D97706; font-weight:800; font-size:1.15rem;">STATUS: ACTION REQUIRED</span>
                    </div>
                    <h2 style="color:#92400E; margin:6px 0 10px 0; font-size:1.6rem;">
                        ⚠️ REQUIRES CUSTOMER CONFIRMATION
                    </h2>
                    <p style="color:#1F2937; font-size:0.98rem; line-height:1.5; margin-bottom:10px;">
                        <b>Policy Rationale:</b><br>{response.reason}
                    </p>
                    <div style="font-size:0.85rem; color:#B45309;">
                        🔔 Step-up authorization prompt dispatched to customer mobile device.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:  # BLOCKED
            revocation_html = ""
            if response.rule_number == "R2" and "revoked_at" in response.details:
                rev_date_str = response.details["revoked_at"]
                revocation_html = f"""
                <div class="revocation-stamp-box">
                    🚨 <b>REVOCATION AUDIT RECORD:</b> Agent revoked on <b>{rev_date_str}</b><br>
                    <i>Revoked agents are permanently prohibited from initiating requests.</i>
                </div>
                """

            st.markdown(
                f"""
                <div class="decision-blocked">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="rule-chip" style="background:#991B1B;">RULE {response.rule_number}</span>
                        <span style="color:#DC2626; font-weight:800; font-size:1.15rem;">STATUS: REJECTED</span>
                    </div>
                    <h2 style="color:#991B1B; margin:6px 0 10px 0; font-size:1.75rem;">
                        ⛔ BLOCKED
                    </h2>
                    {revocation_html}
                    <p style="color:#1F2937; font-size:0.98rem; line-height:1.5; margin-bottom:10px;">
                        <b>Policy Rationale:</b><br>{response.reason}
                    </p>
                    <div style="font-size:0.85rem; color:#991B1B;">
                        ✕ Request terminated at API Gatekeeper perimeter to prevent unauthorized access.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Enforced Rule", response.rule_number)
        m2.metric("Requested Amount", f"₹{amount_inr:,.0f}")
        m3.metric("Customer Limit", f"₹{spending_limit:,.0f}")


# =============================================================================
# TAB 2: AI AGENT MANAGEMENT (Registration, Listing, Revocation)
# =============================================================================
with tab_mgmt:
    st.markdown("### 🤖 Emirates AI Agent Lifecycle Management")
    st.caption(
        "Manage customer-authorized AI agents. Agent registrations and revocations are "
        "permanently recorded in `agents_registry.json` and logged to `audit_log.csv`."
    )

    col_reg, col_rev = st.columns([1, 1], gap="medium")

    # 1. Register AI Agent
    with col_reg:
        with st.container():
            st.markdown(
                """
                <div class="mgmt-card">
                    <div class="section-title">➕ Register New AI Agent</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            reg_customer = st.text_input("Customer Name (Account Owner):", placeholder="e.g. Kavita Sen")
            reg_agent = st.text_input("AI Agent Identifier / Name:", placeholder="e.g. TravelGenie AI")
            reg_notes = st.text_input("Agent Description / Purpose (Optional):", placeholder="e.g. Leisure itinerary booking assistant")

            if st.button("✨ Register AI Agent", type="primary", use_container_width=True):
                success, msg, record = register_agent(
                    agent_name=reg_agent,
                    customer_name=reg_customer,
                    notes=reg_notes,
                )
                if success:
                    st.success(f"✅ {msg}")
                    st.info(f"Registered at: **{record.get('registered_at')}** | Status: **ACTIVE** (Logged to `audit_log.csv`)")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    # 2. Revoke AI Agent
    with col_rev:
        with st.container():
            st.markdown(
                """
                <div class="mgmt-card">
                    <div class="section-title">⛔ Revoke Agent Access</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            current_active_agents = [
                a["agent_name"] for a in list_agents() if a.get("status") == "ACTIVE"
            ]

            if current_active_agents:
                agent_to_revoke = st.selectbox(
                    "Select Active Agent to Revoke:",
                    options=current_active_agents,
                    help="Revoking an agent permanently records date & time, logs to audit_log.csv, and blocks all future requests.",
                )
                revocation_reason = st.text_input(
                    "Revocation Reason (Audit Log):",
                    placeholder="e.g. Unusual booking activity / Customer requested suspension",
                )

                if st.button("🚨 Permanently Revoke Agent", use_container_width=True):
                    success, msg, rev_timestamp = revoke_agent(
                        agent_name=agent_to_revoke,
                        reason=revocation_reason,
                    )
                    if success:
                        st.error(f"⛔ {msg}")
                        st.warning(f"Exact Revocation Timestamp Saved: **{rev_timestamp}** (Logged to `audit_log.csv`)")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
            else:
                st.info("No currently ACTIVE agents available to revoke.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. List All Agents Table
    st.markdown("#### 📋 Registered AI Agents (Saved in `agents_registry.json`)")
    all_agents = list_agents()

    if all_agents:
        formatted_list = []
        for a in all_agents:
            status_symbol = "🟢 ACTIVE" if a.get("status") == "ACTIVE" else "🔴 REVOKED"
            rev_time_disp = a.get("revoked_at") if a.get("revoked_at") else "— (Active)"
            formatted_list.append(
                {
                    "AI Agent Name": a.get("agent_name"),
                    "Customer Name": a.get("customer_name"),
                    "Status": status_symbol,
                    "Registration Date & Time": a.get("registered_at", "—"),
                    "Revocation Date & Time": rev_time_disp,
                    "Notes / Audit Details": a.get("notes") or a.get("revocation_reason") or "—",
                }
            )

        df_agents = pd.DataFrame(formatted_list)
        st.dataframe(df_agents, use_container_width=True, hide_index=True)

        col_json_dl, col_json_path = st.columns([1, 1])
        with col_json_dl:
            json_str = json.dumps(load_agents_registry(), indent=4)
            st.download_button(
                label="📥 Download Registry (JSON)",
                data=json_str,
                file_name="agents_registry.json",
                mime="application/json",
            )
        with col_json_path:
            st.caption(f"📁 **Persistent File Location:** `{get_default_registry_path()}`")


# =============================================================================
# TAB 3: SAMPLE TEST CASES (Expected vs. Actual Matrix)
# =============================================================================
with tab_testcases:
    st.markdown("### 🧪 Six Core Sample Test Cases (Expected vs. Actual Decisions)")
    st.caption(
        "Demonstrates comprehensive policy coverage across unknown agents, revoked agents, active agent fare searches, "
        "bookings within/above ₹20,000, flight changes, and refunds."
    )

    test_results = run_sample_test_cases()
    all_passed = all(t["status"] == "PASS" for t in test_results)

    if all_passed:
        st.success("🎉 **VERIFICATION COMPLETE:** All sample test cases passed with a 100% match between Expected and Actual gatekeeper decisions!")
    else:
        st.error("⚠️ Some test cases did not match expected decisions.")

    # Render interactive test cases cards
    for t in test_results:
        status_color = "#10B981" if t["status"] == "PASS" else "#EF4444"
        with st.expander(f"{t['id']}: {t['name']} [Target Rule: {t['rule_target']}] — {t['status']}", expanded=True):
            col_tc_info, col_tc_compare = st.columns([1.2, 1.0])
            with col_tc_info:
                st.markdown(f"**Policy Objective:** {t['description']}")
                st.markdown(
                    f"• **Customer:** `{t['customer']}` | **Agent:** `{t['agent']}`<br>"
                    f"• **Action:** `{t['action']}` | **Amount:** `₹{t['amount']:,.2f}` | **Customer Limit:** `₹{t['spending_limit']:,.2f}`",
                    unsafe_allow_html=True,
                )
                if st.button(f"📥 Load {t['id']} into Gatekeeper Form", key=f"load_{t['id']}"):
                    st.session_state.customer_name_input = t["customer"]
                    st.session_state.agent_name_input = t["agent"]
                    st.session_state.action_input = t["action"]
                    st.session_state.amount_input = float(t["amount"])
                    st.session_state.spending_limit_input = float(t["spending_limit"])
                    st.success(f"Loaded {t['id']} into Gatekeeper! Switch to the 'Request Gatekeeper' tab to evaluate.")

            with col_tc_compare:
                st.markdown(
                    f"""
                    <div style="background:#F9FAFB; padding:12px; border-radius:8px; border:1px solid #E5E7EB;">
                        <div style="display:flex; justify-content:space-between;">
                            <b>Expected Decision:</b> <span style="font-weight:700;">{t['expected_decision']} ({t['expected_rule']})</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:4px;">
                            <b>Actual Decision:</b> <span style="font-weight:700; color:{status_color};">{t['actual_decision']} ({t['actual_rule']})</span>
                        </div>
                        <div style="margin-top:6px; font-size:0.85rem; color:#4B5563;">
                            <b>Actual Reason:</b><br>{t['actual_reason']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Action to log all test cases to audit log
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Run & Log All Sample Test Cases to audit_log.csv", use_container_width=True):
        for t in test_results:
            log_audit_event(
                customer_name=t["customer"],
                agent_name=t["agent"],
                action=t["action"],
                amount_inr=t["amount"],
                final_decision=t["actual_decision"],
                rule_number=t["actual_rule"],
                reason=f"[Automated Test Verification] {t['actual_reason']}",
            )
        st.success("✅ All sample test cases were evaluated and appended to `audit_log.csv`! Switch to the 'Audit Log Dashboard' tab to review them.")
        st.rerun()


# =============================================================================
# TAB 4: AUDIT LOG DASHBOARD (Permanent Append-Only audit_log.csv)
# =============================================================================
with tab_audit:
    st.markdown("### 📊 Permanent Audit Log Dashboard (`audit_log.csv`)")
    st.caption(
        "Permanent, append-only chronological record of all agent requests, registrations, and revocations. "
        "Old records are permanently preserved and never overwritten."
    )

    df_audit = load_audit_log()

    # KPI Metrics Row
    if not df_audit.empty:
        total_records = len(df_audit)
        allowed_records = len(df_audit[df_audit["Final Decision"] == "ALLOWED"])
        confirmation_records = len(df_audit[df_audit["Final Decision"] == "REQUIRES CONFIRMATION"])
        blocked_records = len(df_audit[df_audit["Final Decision"] == "BLOCKED"])
        lifecycle_records = len(df_audit[df_audit["Final Decision"].isin(["REGISTERED", "REVOKED"])])

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Events Logged", total_records)
        k2.metric("✅ Allowed", allowed_records)
        k3.metric("⚠️ Confirmation Req.", confirmation_records)
        k4.metric("⛔ Blocked", blocked_records)
        k5.metric("🤖 Lifecycle Events", lifecycle_records)

        st.divider()

        # Filters and search
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            decision_choices = ["All Decisions"] + sorted(list(df_audit["Final Decision"].unique()))
            chosen_decision = st.selectbox("Filter by Decision:", decision_choices)
        with f2:
            action_choices = ["All Actions"] + sorted(list(df_audit["Requested Action"].unique()))
            chosen_action = st.selectbox("Filter by Action:", action_choices)
        with f3:
            search_query = st.text_input("🔍 Search Customer, Agent, or Reason:", placeholder="Type name or keyword...")

        # Apply filtering
        filtered_df = df_audit.copy()
        if chosen_decision != "All Decisions":
            filtered_df = filtered_df[filtered_df["Final Decision"] == chosen_decision]
        if chosen_action != "All Actions":
            filtered_df = filtered_df[filtered_df["Requested Action"] == chosen_action]
        if search_query:
            query = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["Customer Name"].str.lower().str.contains(query, na=False)
                | filtered_df["AI Agent Name"].str.lower().str.contains(query, na=False)
                | filtered_df["Reason"].str.lower().str.contains(query, na=False)
            ]

        # Display dataframe in reverse-chronological order (latest first)
        st.markdown(f"**Showing `{len(filtered_df)}` of `{total_records}` records:**")
        st.dataframe(
            filtered_df.iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

        col_csv_dl, col_csv_info = st.columns([1, 1])
        with col_csv_dl:
            raw_csv_path = get_default_audit_log_path()
            if raw_csv_path.exists():
                with open(raw_csv_path, "rb") as f:
                    csv_bytes = f.read()
                st.download_button(
                    label="📥 Download audit_log.csv",
                    data=csv_bytes,
                    file_name="audit_log.csv",
                    mime="text/csv",
                )
        with col_csv_info:
            st.caption(f"📁 **Persistent File Location:** `{get_default_audit_log_path()}` (Append-Only)")

    else:
        st.info("No audit records in `audit_log.csv` yet. Submit a request using the 'Request Gatekeeper' or register an agent to generate records.")


# =============================================================================
# TAB 5: POLICY RULES MATRIX (R1 to R8)
# =============================================================================
with tab_rules:
    st.markdown(
        """
        ### 📋 Emirates Agent Gatekeeper Policy Rules Matrix (R1 – R8)
        
        This policy engine enforces eight governance rules for autonomous AI agents interacting with Emirates services:

        | Rule | Title | Condition | Gatekeeper Decision | MBA Governance & Risk Rationale |
        |---|---|---|---|---|
        | **R1** | **Unknown Agent Blocked** | Agent not registered in Emirates trust store | **BLOCKED** | **Perimeter Security:** Rejects unauthenticated third-party bots to prevent spoofing and data leaks. |
        | **R2** | **Revoked Agent Blocked** | Agent credentials marked as `REVOKED` | **BLOCKED** | **Permanent Threat Isolation:** Never permits revoked bots to make requests; displays exact revocation timestamp for audit compliance. |
        | **R3** | **View Fares Allowed** | Known active agent requesting search | **ALLOWED** | **Read-Only Autonomy:** Non-state-altering search operations pose no direct financial liability. |
        | **R4** | **Booking within Limit** | Booking ≤ ₹20,000 AND ≤ Customer Spending Limit | **ALLOWED** | **Bounded Autonomy:** Enables low-friction automated ticketing within customer-delegated budget. |
        | **R4 (Exceed)** | **Booking Exceeds Limit** | Booking ≤ ₹20,000 BUT > Customer Spending Limit | **BLOCKED** | **Customer Financial Protection:** Prevents agents from breaching personalized customer limits. |
        | **R5** | **Booking above ₹20,000** | Booking > ₹20,000 | **REQUIRES CONFIRMATION** | **High-Value Fraud Control:** Mandatory customer-in-the-loop verification (2FA) for major financial commitments. |
        | **R6** | **Changing Flight** | Action is 'Change flight' | **REQUIRES CONFIRMATION** | **Itinerary Integrity:** Prevents autonomous agents from inadvertently rescheduling confirmed flights. |
        | **R7** | **Refund Requests** | Action is 'Refund' | **REQUIRES CONFIRMATION** | **Non-Repudiation:** Protects passengers from unauthorized cancellations and cancellation penalty fees. |
        | **R8** | **Invalid Requests Blocked** | Blank fields, negative amounts, or malformed data | **BLOCKED** | **API Robustness:** Rejects malformed agent payloads before downstream processing. |
        """
    )

# -----------------------------------------------------------------------------
# Educational Simulation Disclaimer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="disclaimer-banner">
        ⚠️ <b>EDUCATIONAL SIMULATION NOTICE:</b> This project was created exclusively for academic evaluation as part of
        an MBA curriculum (Student Enrolment No: <b>PGD202566060</b>). It does not connect to real Emirates airline operational
        systems, APIs, or payment gateways. No real monetary transactions are processed.
    </div>
    """,
    unsafe_allow_html=True,
)
