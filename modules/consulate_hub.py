# ============================================================================
# DIGITAL CONSULATE HUB™ MODULE
# Consulaire diensten: documenten, beurzen, investeringen, assistentie
# ============================================================================

import streamlit as st
import os
import uuid
from datetime import datetime

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import Options, Messages, VAULT_DIR, MAX_FILE_SIZE_MB
from database.connection import get_data, run_query, check_duplicate_id
from utils.helpers import sanitize_id, sanitize_filename, get_identity_names_map, generate_uuid
from auth.security import log_audit
from ui.components import metric_row, page_header


def render(username: str):
    """Render de Digital Consulate Hub module."""
    
    page_header(
        " Digital Consulate Hub™",
        "Complete Consular Services: Documents, Scholarships, Investments & Assistance"
    )
    
    tab1, tab2, tab3, tab4 = st.tabs([
        " Document Vault", 
        " Scholarships", 
        " Investments", 
        "🆘 Assistance"
    ])
    
    with tab1:
        render_document_vault(username)
    
    with tab2:
        render_scholarships(username)
    
    with tab3:
        render_investments()
    
    with tab4:
        render_assistance(username)


def render_document_vault(username: str):
    """Render document vault tab."""
    
    with st.expander(" Upload Sovereign Document", expanded=False):
        with st.form("vault_upload"):
            col1, col2 = st.columns(2)
            
            with col1:
                doc_id = st.text_input("Document ID", placeholder="e.g., PIX-2025-001")
                doc_type = st.selectbox("Type", Options.DOCUMENT_TYPES)
            
            with col2:
                status = st.selectbox(t("status"), Options.DOCUMENT_STATUSES)
                file = st.file_uploader("Select File", type=['pdf', 'jpg', 'png', 'jpeg'])
            
            if st.form_submit_button(" SECURE DOCUMENT", width="stretch"):
                sid = sanitize_id(doc_id)
                
                if not file:
                    st.error(Messages.FILE_REQUIRED)
                elif not sid:
                    st.error(Messages.INVALID_ID)
                elif check_duplicate_id(sid, 'consular_registry'):
                    st.error(Messages.DUPLICATE_ID.format(sid))
                elif file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    st.error(Messages.FILE_TOO_LARGE.format(MAX_FILE_SIZE_MB))
                else:
                    fname = sanitize_filename(file.name)
                    unique_fname = f"{uuid.uuid4().hex[:8]}_{fname}"
                    fpath = os.path.join(VAULT_DIR, f"{sid}_{unique_fname}")
                    
                    with open(fpath, "wb") as f:
                        f.write(file.getbuffer())
                    
                    success = run_query(
                        "INSERT INTO consular_registry VALUES (?, ?, ?, ?, ?)",
                        (sid, doc_type, unique_fname, status, datetime.now().isoformat())
                    )
                    
                    if success:
                        st.success(Messages.DOCUMENT_SECURED.format(fname))
                        log_audit(username, "DOCUMENT_UPLOADED", "Consulate Hub")
                        st.rerun()
    
    st.divider()
    
    # Search and filter
    col_search, col_status = st.columns([3, 1])
    with col_search:
        search_q = st.text_input(" Search", "", placeholder="Search by ID or filename...")
    with col_status:
        status_filter = st.selectbox(t("filter"), ["All"] + Options.DOCUMENT_STATUSES)
    
    # Document list
    df = get_data("consular_registry")
    
    if not df.empty:
        filtered_df = df.copy()
        
        if search_q:
            q = search_q.lower()
            filtered_df = filtered_df[
                filtered_df['id'].str.lower().str.contains(q) | 
                filtered_df['filename'].str.lower().str.contains(q)
            ]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        if filtered_df.empty:
            st.info(" No documents match search criteria.")
        else:
            st.write(f"###  Documents ({len(filtered_df)} found)")
            
            for idx, row in filtered_df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 0.5])
                
                c1.write(f"**`{row['id']}`**")
                
                display_name = row['filename'].split('_', 1)[-1] if '_' in row['filename'] else row['filename']
                c2.write(f"{display_name} • {row['doc_type']}")
                c3.write(row['status'])
                
                fpath = os.path.join(VAULT_DIR, f"{row['id']}_{row['filename']}")
                
                if os.path.exists(fpath):
                    try:
                        with open(fpath, "rb") as f:
                            c4.download_button("", f.read(), file_name=display_name, key=f"dl_{row['id']}")
                    except:
                        c4.write("")
                else:
                    c4.write("")
                
                if c5.button("", key=f"del_{row['id']}"):
                    try:
                        if os.path.exists(fpath):
                            os.remove(fpath)
                        run_query("DELETE FROM consular_registry WHERE id = ?", (row['id'],))
                        log_audit(username, "DOCUMENT_DELETED", "Consulate Hub")
                        st.success(f" Document {row['id']} deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f" Error: {e}")
    else:
        st.info(" Vault is empty.")


def render_scholarships(username: str):
    """Render scholarships tab."""
    
    st.subheader(" Scholarship Application System")
    
    id_map = get_identity_names_map()
    
    with st.form("scholarship_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            if id_map:
                applicant_id = st.selectbox(
                    "Applicant Identity", 
                    list(id_map.keys()), 
                    format_func=lambda x: id_map.get(x, x)
                )
            else:
                st.warning("No identities registered yet.")
                applicant_id = None
            
            scholarship_type = st.selectbox("Scholarship Type", Options.SCHOLARSHIP_TYPES)
        
        with col2:
            university = st.text_input("University/Institution", placeholder="e.g., Mohammed V University")
            field = st.text_input("Field of Study", placeholder="e.g., Computer Science")
        
        amount = st.number_input("Requested Amount (€)", min_value=0.0, step=500.0, value=5000.0)
        
        if st.form_submit_button(" SUBMIT APPLICATION", width="stretch"):
            if not applicant_id or not university or not field:
                st.error(" All fields required.")
            elif amount <= 0:
                st.error(" Amount must be positive.")
            else:
                app_id = generate_uuid("SCH")
                
                success = run_query(
                    "INSERT INTO scholarship_applications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (app_id, applicant_id, scholarship_type, university, field, "PENDING", amount, 
                     None, datetime.now().isoformat(), None, None)
                )
                
                if success:
                    st.success(Messages.APPLICATION_SUBMITTED.format(app_id))
                    st.info("You will be notified via email when your application is reviewed.")
                    log_audit(username, "SCHOLARSHIP_APPLIED", "Consulate Hub")
                    st.rerun()
    
    st.divider()
    
    # Application overview
    df_scholarships = get_data("scholarship_applications")
    
    if not df_scholarships.empty:
        st.write(f"###  Total Applications: {len(df_scholarships)}")
        
        pending = len(df_scholarships[df_scholarships['status'] == 'PENDING'])
        approved = len(df_scholarships[df_scholarships['status'] == 'APPROVED'])
        rejected = len(df_scholarships[df_scholarships['status'] == 'REJECTED'])
        
        metric_row([
            ("⏳ Pending", pending),
            (" Approved", approved),
            (" Rejected", rejected),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.dataframe(df_scholarships, width="stretch", hide_index=True)
    else:
        st.info("No scholarship applications yet.")


def render_investments():
    """Render investments tab."""
    
    st.subheader(" Diaspora Investment Tracking")
    st.info("Investment tracking system for diaspora community. Track capital inflows, project investments, and ROI.")
    
    df_investments = get_data("financial_records")
    investment_data = df_investments[df_investments['type'] == 'Investment Inbound'] if not df_investments.empty else None
    
    if investment_data is not None and not investment_data.empty:
        st.write(f"###  Active Investments: {len(investment_data)}")
        
        total_invested = investment_data['amount'].sum()
        avg_investment = investment_data['amount'].mean()
        num_investors = investment_data['entity_id'].nunique()
        
        metric_row([
            (" Total Invested", f"€ {total_invested:,.0f}"),
            (" Avg Investment", f"€ {avg_investment:,.0f}"),
            (" Investors", num_investors),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        display_inv = investment_data.copy()
        display_inv['amount'] = display_inv['amount'].apply(lambda x: f"€ {x:,.2f}")
        st.dataframe(display_inv, width="stretch", hide_index=True)
        
        st.write("###  Investments by Sector")
        sector_inv = investment_data.groupby("sector")["amount"].sum()
        st.bar_chart(sector_inv)
    else:
        st.info("No investment records. Log investments in Foundation Bank module.")


def render_assistance(username: str):
    """Render assistance tab."""
    
    st.subheader("🆘 Consular Assistance Ticketing")
    
    id_map = get_identity_names_map()
    
    with st.form("assistance_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            if id_map:
                requester_id = st.selectbox(
                    "Your Identity", 
                    list(id_map.keys()), 
                    format_func=lambda x: id_map.get(x, x)
                )
            else:
                st.warning("No identities registered yet.")
                requester_id = None
            
            assist_type = st.selectbox("Assistance Type", Options.ASSISTANCE_TYPES)
        
        with col2:
            urgency = st.selectbox("Urgency Level", Options.URGENCY_LEVELS)
        
        description = st.text_area(
            "Describe your situation", 
            placeholder="Please provide details about your assistance request..."
        )
        
        if st.form_submit_button("🆘 SUBMIT REQUEST", width="stretch"):
            if not requester_id or not description.strip():
                st.error(" Identity and description required.")
            else:
                ticket_id = generate_uuid("AST")
                
                success = run_query(
                    "INSERT INTO consular_assistance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (ticket_id, requester_id, assist_type, description, urgency, "OPEN", 
                     datetime.now().isoformat(), None, None)
                )
                
                if success:
                    st.success(Messages.ASSISTANCE_CREATED.format(ticket_id))
                    st.info("A consular officer will contact you within 24-48 hours (urgent cases within 2 hours).")
                    log_audit(username, "ASSISTANCE_REQUESTED", "Consulate Hub")
                    st.rerun()
    
    st.divider()
    
    # Assistance overview
    df_assistance = get_data("consular_assistance")
    
    if not df_assistance.empty:
        st.write("###  Your Assistance Requests")
        
        total_tickets = len(df_assistance)
        open_tickets = len(df_assistance[df_assistance['status'] == 'OPEN'])
        high_urgency = len(df_assistance[(df_assistance['urgency'] == 'HIGH') & (df_assistance['status'] == 'OPEN')])
        
        metric_row([
            (" Total Tickets", total_tickets),
            (" Open", open_tickets),
            (" High Urgency", high_urgency),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Open tickets
        open_only = df_assistance[df_assistance['status'] == 'OPEN']
        
        if not open_only.empty:
            for idx, ticket in open_only.iterrows():
                urgency_color = "" if ticket['urgency'] == "HIGH" else "" if ticket['urgency'] == "MEDIUM" else ""
                
                with st.expander(f"{urgency_color} {ticket['ticket_id']} - {ticket['assistance_type']} ({ticket['created_at'][:10]})"):
                    st.write(f"**Description:** {ticket['description']}")
                    st.write(f"**Status:** {ticket['status']}")
                    st.write(f"**Created:** {ticket['created_at']}")
                    
                    if ticket['assigned_to']:
                        st.write(f"**Assigned to:** {ticket['assigned_to']}")
        else:
            st.success("No open assistance requests.")
        
        # Resolved tickets
        resolved = df_assistance[df_assistance['status'] != 'OPEN']
        if not resolved.empty:
            with st.expander(f" Resolved Tickets ({len(resolved)})"):
                st.dataframe(resolved, width="stretch", hide_index=True)
    else:
        st.info("No assistance requests yet.")
