import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from fpdf import FPDF
import io

# Company Info
COMPANY_NAME = "FinElevate India"
ADVISOR_NAME = "Chirag Sanghvi"
PHONE_NUMBER = "+91-7744892728"
EMAIL = "finelevateindia@gmail.com"
WEBSITE = "www.finelevateindia.com"
LICENSE_NO = "SEBI REG: INH000000000"

# Set page config
st.set_page_config(
    page_title="Wealth Health Check - FinElevate India",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS to increase sidebar width ---
st.markdown(
    """
    <style>
    .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
h1 {
    font-size: 1.9rem;
    font-weight: 600;
    color: #284157;
    margin-bottom: 0.3rem;
}
h2 {
    color: #284157;
    margin-top: 1rem;
    font-weight: 600;
}
.section-box {
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgb(40 65 87 / 0.1);
    margin-bottom: 25px;
}
.subtle-text {
    color: #555;
    font-size: 0.9rem;
    font-style: italic;
    margin-top: 10px;
}
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper: Clean text for PDF to avoid latin-1 encode error
def clean_text_for_pdf(text):
    replacements = {
        '\u2013': '-',   # en dash
        '\u2014': '-',   # em dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...', # ellipsis
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    text = text.encode('latin-1', errors='ignore').decode('latin-1')
    return text


# Currency formatting in Indian system
def format_currency(amount):
    if amount >= 1e7:  # crore
        return f"₹{amount/1e7:.2f} Cr"
    elif amount >= 1e5:  # lakh
        return f"₹{amount/1e5:.2f} L"
    else:
        return f"₹{amount:,.0f}"


# Create textual progress bar for console-like visual
def create_text_bar(percentage, width=30):
    filled = int(percentage * width / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {percentage:.1f}%"


# Pie chart of asset allocation with Plotly
def asset_allocation_pie(labels, values):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
    fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    fig.update_layout(margin=dict(t=40,b=10,l=10,r=10), height=350)
    return fig


# PDF report generation
def generate_pdf_report(client_name, age, annual_income, portfolio_details, recommendations, risk_profile):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Comprehensive Wealth Health Check", 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, COMPANY_NAME, 0, 1, "C")
    pdf.cell(0, 6, LICENSE_NO, 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, clean_text_for_pdf(f"Client: {client_name}"), 0, 1)
    pdf.cell(0, 7, clean_text_for_pdf(f"Age: {age}"), 0, 1)
    pdf.cell(0, 7, clean_text_for_pdf(f"Annual Income: {format_currency(annual_income)}"), 0, 1)
    pdf.cell(0, 7, clean_text_for_pdf(f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}"), 0, 1)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "Portfolio Details:", 0, 1)
    pdf.set_font("Arial", "", 12)
    for asset, val in portfolio_details.items():
        pdf.cell(0, 7, clean_text_for_pdf(f"  - {asset}: {format_currency(val)}"), 0, 1)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "Recommendations:", 0, 1)
    pdf.set_font("Arial", "", 12)
    for rec in recommendations:
        pdf.multi_cell(0, 7, clean_text_for_pdf(f" - {rec}"))
    pdf.ln(6)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "Risk Profile:", 0, 1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, clean_text_for_pdf(risk_profile))

    pdf.ln(15)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 5, clean_text_for_pdf("Disclaimer: This analysis is for informational purposes only. Past performance does not guarantee future results."), 0, 1, "C")
    pdf.cell(0, 5, clean_text_for_pdf("Please consult with a qualified advisor before making investment decisions."), 0, 1, "C")
    return pdf.output(dest='S').encode('latin1')


# --- UI Begins ---

# Header on main area
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("💼")  # You can replace with st.image('logo.png', width=80) if you have a logo
with col2:
    st.markdown(f"## Comprehensive Wealth Health Check")
    st.markdown(f"**{COMPANY_NAME}**  |  {LICENSE_NO}")
    st.markdown(f"📱 {PHONE_NUMBER}  |  📧 {EMAIL}  |  🌐 {WEBSITE}")

# Sidebar client and portfolio inputs
st.sidebar.header("Client Details & Portfolio Input")

client_name = st.sidebar.text_input("Client Name")
age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=30)
annual_income_lakhs = st.sidebar.number_input("Annual Income (₹ in lakhs)", min_value=0.0, step=0.5)

st.sidebar.markdown("### Portfolio Value (₹ in lakhs)")
equity_value = st.sidebar.number_input("Direct Stocks Value", min_value=0.0)
mutual_funds = st.sidebar.number_input("Mutual Funds Value", min_value=0.0)
fd_value = st.sidebar.number_input("Fixed Deposits", min_value=0.0)
ppf_value = st.sidebar.number_input("PPF/EPF", min_value=0.0)
bonds_value = st.sidebar.number_input("Bonds/Debt Funds", min_value=0.0)
real_estate = st.sidebar.number_input("Real Estate Value", min_value=0.0)
gold_value = st.sidebar.number_input("Gold/Commodities", min_value=0.0)
cash_savings = st.sidebar.number_input("Cash/Savings Account", min_value=0.0)
life_insurance = st.sidebar.number_input("Life Insurance Cover (₹ in lakhs)", min_value=0.0)
health_insurance = st.sidebar.number_input("Health Insurance Cover (₹ in lakhs)", min_value=0.0)

analyze = st.sidebar.button("Analyze Portfolio")

if analyze:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    if not client_name.strip():
        st.error("Please enter Client Name.")
    else:
        annual_income = annual_income_lakhs * 100000
        equity_total = (equity_value + mutual_funds) * 100000
        debt_total = (fd_value + ppf_value + bonds_value) * 100000
        real_estate_val = real_estate * 100000
        gold_val = gold_value * 100000
        cash_val = cash_savings * 100000
        life_cover = life_insurance * 100000
        health_cover = health_insurance * 100000
        total_portfolio = equity_total + debt_total + real_estate_val + gold_val + cash_val

        if total_portfolio <= 0:
            st.error("Please enter portfolio values greater than zero for analysis.")
        else:
            st.subheader(f"Analysis Report for {client_name}")
            st.write(f"Date of Analysis: {datetime.now().strftime('%B %d, %Y')}")
            st.write(f"Total Portfolio Value: {format_currency(total_portfolio)}")
            st.write(f"Annual Income: {format_currency(annual_income)}")

            # Asset allocation percentages
            equity_pct = equity_total * 100 / total_portfolio
            debt_pct = debt_total * 100 / total_portfolio
            real_estate_pct = real_estate_val * 100 / total_portfolio
            gold_pct = gold_val * 100 / total_portfolio
            cash_pct = cash_val * 100 / total_portfolio

            # Plot asset allocation pie chart
            labels = ['Equity & Mutual Funds', 'Fixed Income', 'Real Estate', 'Gold/Commodities', 'Cash & Savings']
            values = [equity_total, debt_total, real_estate_val, gold_val, cash_val]
            fig = asset_allocation_pie(labels, values)
            st.plotly_chart(fig, use_container_width=True)

            # Show detailed allocation bars
            st.markdown("#### Current Asset Allocation")
            st.text(f"Equity & MF:      {create_text_bar(equity_pct)}")
            st.text(f"Fixed Income:     {create_text_bar(debt_pct)}")
            st.text(f"Real Estate:      {create_text_bar(real_estate_pct)}")
            st.text(f"Gold:             {create_text_bar(gold_pct)}")
            st.text(f"Cash & Savings:   {create_text_bar(cash_pct)}")

            # Prepare recommendations list for PDF and display
            recommendations = []

            st.markdown("### Recommendations")

            # Equity allocation vs age
            ideal_equity = 100 - age
            if equity_pct < ideal_equity - 10:
                warning_msg = (f"Under-allocated in Equity: Current {equity_pct:.1f}%, "
                               f"Ideal {ideal_equity}%. Consider investing more in equity instruments.")
                st.warning(warning_msg)
                recommendations.append(warning_msg)
            elif equity_pct > ideal_equity + 10:
                warning_msg = (f"Over-allocated in Equity: Current {equity_pct:.1f}%, "
                               f"Ideal {ideal_equity}%. Consider rebalancing to debt instruments.")
                st.warning(warning_msg)
                recommendations.append(warning_msg)
            else:
                success_msg = f"Equity allocation is optimal based on age ({equity_pct:.1f}%)."
                st.success(success_msg)
                recommendations.append(success_msg)

            # Emergency fund check
            monthly_expense = annual_income * 0.7 / 12
            required_emergency = monthly_expense * 6
            if cash_val < required_emergency:
                shortfall = required_emergency - cash_val
                error_msg = f"Emergency fund is insufficient by {format_currency(shortfall)}. Increase savings."
                st.error(error_msg)
                recommendations.append(error_msg)
            else:
                months_covered = cash_val / monthly_expense
                success_msg = f"Emergency fund is adequate covering {months_covered:.1f} months of expenses."
                st.success(success_msg)
                recommendations.append(success_msg)

            # Life insurance adequacy
            required_life_cover = annual_income * 10
            if life_cover < required_life_cover:
                gap = required_life_cover - life_cover
                error_msg = f"Life insurance cover is insufficient by {format_currency(gap)}. Please increase coverage."
                st.error(error_msg)
                recommendations.append(error_msg)
            else:
                success_msg = f"Life insurance cover is adequate at {life_cover / annual_income:.1f}x annual income."
                st.success(success_msg)
                recommendations.append(success_msg)

            # Health insurance adequacy
            min_health_cover = 1000000  # ₹10 Lakhs
            if health_cover < min_health_cover:
                warning_msg = ("Health insurance cover is below recommended ₹10L. "
                               "Consider upgrading your health cover.")
                st.warning(warning_msg)
                recommendations.append(warning_msg)
            else:
                success_msg = "Health insurance cover is adequate."
                st.success(success_msg)
                recommendations.append(success_msg)

            # Risk Profile
            st.markdown("### Portfolio Risk Assessment")
            if equity_pct > 80:
                risk_level = "Aggressive 🔴"
                risk_desc = "High volatility, high potential returns."
            elif equity_pct > 60:
                risk_level = "Moderate-Aggressive 🟡"
                risk_desc = "Moderate to high volatility, good growth potential."
            elif equity_pct > 40:
                risk_level = "Moderate 🟢"
                risk_desc = "Balanced risk-return profile."
            else:
                risk_level = "Conservative 🔵"
                risk_desc = "Low volatility, steady returns."
            st.write(f"Risk Profile: **{risk_level}**")
            st.write(risk_desc)

            risk_profile_text = f"{risk_level}\n{risk_desc}"

            # Footer
            st.markdown("---")
            st.write(f"Report prepared by: {ADVISOR_NAME} | {COMPANY_NAME}")
            st.write(f"Contact: {PHONE_NUMBER} | Email: {EMAIL} | Website: {WEBSITE}")
            st.caption("Disclaimer: This analysis is for informational purposes only. Past performance does not guarantee future results. "
                       "Please consult with a qualified advisor before making investment decisions.")

            # Generate PDF Button
            pdf_bytes = generate_pdf_report(
                client_name=client_name,
                age=age,
                annual_income=annual_income,
                portfolio_details={
                    "Equity & Mutual Funds": equity_total,
                    "Fixed Income": debt_total,
                    "Real Estate": real_estate_val,
                    "Gold/Commodities": gold_val,
                    "Cash & Savings": cash_val,
                    "Life Insurance Cover": life_cover,
                    "Health Insurance Cover": health_cover
                },
                recommendations=recommendations,
                risk_profile=risk_profile_text,
            )

            st.download_button(
                label="📄 Download Full Report (PDF)",
                data=pdf_bytes,
                file_name=f"wealth_health_check_{client_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                help="Download a professional PDF report to share or archive.",
            )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Please enter client details and portfolio information, then click 'Analyze Portfolio' from the sidebar to see the report.")
