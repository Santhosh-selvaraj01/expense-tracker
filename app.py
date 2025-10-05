import streamlit as st

# ---- Simple Login ----
PASSWORD = "Mit@12345678"  # <-- change this to a strong password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    password_input = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Incorrect password")
    st.stop()  # stops the rest of the app until login



import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests

DB = "expenses.db"

# -------------------- TELEGRAM CONFIG -------------------- #
TELEGRAM_TOKEN = "7071118483:AAHN5QXb9cKeLJFDiLEWzKO8b1JLwbGvCHg"
CHAT_ID = 1430612355

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    return response.ok

def get_summary_message(selected_month="All Time"):
    """Return a formatted summary message (monthly or all time)."""
    income_df = fetch_df("SELECT * FROM income")
    exp_df = fetch_df("SELECT * FROM expenses")

    if selected_month != "All Time":
        income_df = income_df[income_df['month'] == selected_month]
        exp_df = exp_df[pd.to_datetime(exp_df['date']).dt.to_period('M').astype(str) == selected_month]

    total_income = income_df['amount'].sum() if not income_df.empty else 0
    total_expenses = exp_df['amount'].sum() if not exp_df.empty else 0
    net_savings = total_income - total_expenses

    # Format month display
    if selected_month == "All Time":
        month_label = "All Time"
    else:
        try:
            month_label = pd.Period(selected_month).strftime("%b %Y")
        except:
            month_label = selected_month

    message = f"💰 *Expense Tracker Summary* ({month_label})\n\n"
    message += f"📈 *Total Income:* ₹{total_income:,.2f}\n"
    message += f"💸 *Total Expenses:* ₹{total_expenses:,.2f}\n"
    message += f"💎 *Net Savings:* ₹{net_savings:,.2f}\n\n"

    if not exp_df.empty:
        message += "🏷️ *Expenses by Category:*\n"
        for cat, amt in exp_df.groupby("category")['amount'].sum().items():
            message += f"• {cat}: ₹{amt:,.2f}\n"
        message += "\n🔹 *Expenses by Sub-category:*\n"
        for sub, amt in exp_df.groupby("sub_category")['amount'].sum().items():
            message += f"• {sub}: ₹{amt:,.2f}\n"
    else:
        message += "No expenses recorded yet."

    return message

# -------------------- CREDIT CARD DATES -------------------- #
credit_card_dates = {
    "ICICI Amazon": {"statement": 28, "payment": 15},
    "ICICI Raga": {"statement": 28, "payment": 15},
    "Tata Neu": {"statement": 1, "payment": 21},
    "HDFC Millina": {"statement": 14, "payment": 4},
    "IDFC Petrol": {"statement": 19, "payment": 9},
    "Axis Bank Neo": {"statement": 10, "payment": 30},
    "Axis Petrol": {"statement": 17, "payment": 6},
    "Axis My Zone": {"statement": 20, "payment": 9},
    "IDFC Select": {"statement": 20, "payment": 4},
    "IndusInd": {"statement": 15, "payment": 5},
    "SBI": {"statement": 21, "payment": 10}
}

# -------------------- CATEGORIES -------------------- #
main_categories = ["Rent", "Credit Card", "Utilities", "Education", "Investments", "Misc"]
sub_categories_dict = {
    "Rent": ["Home", "Others"],
    "Credit Card": list(credit_card_dates.keys()),
    "Utilities": ["Electricity", "Food", "Groceries", "Others"],
    "Education": ["School", "Others"],
    "Investments": ["Gold", "Silver", "LIC", "FD", "RD", "Mutual Fund", "Crypto", "Others"],
    "Misc": []
}

# -------------------- UTILITY FUNCTIONS -------------------- #
def run_query(query, params=()):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_df(query):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# -------------------- SIDEBAR -------------------- #
st.sidebar.title("💰 Expense Tracker")
page = st.sidebar.radio("Go to", ["Summary", "Add Income", "Add Expense", "View Data", "Monthly Comparison", "Yearly Comparison"])

# -------------------- SUMMARY -------------------- #
if page == "Summary":
    st.header("📊 Summary Dashboard")

    income_df = fetch_df("SELECT * FROM income")
    exp_df = fetch_df("SELECT * FROM expenses")

    if not exp_df.empty:
        exp_df['date'] = pd.to_datetime(exp_df['date'])
        exp_df['month'] = exp_df['date'].dt.to_period('M')
    if not income_df.empty:
        income_df['month'] = pd.to_datetime(income_df['month']).dt.to_period('M')

    all_months = sorted(list(set(exp_df['month'].astype(str).tolist() + income_df['month'].astype(str).tolist())))

    if all_months:
        selected_month = st.selectbox("Select Month for Summary", ["All Time"] + all_months, index=len(all_months))
        if selected_month != "All Time":
            income_month = income_df[income_df['month'].astype(str) == selected_month] if not income_df.empty else pd.DataFrame()
            exp_month = exp_df[exp_df['month'].astype(str) == selected_month] if not exp_df.empty else pd.DataFrame()
        else:
            income_month, exp_month = income_df, exp_df

        total_income = income_month['amount'].sum() if not income_month.empty else 0
        total_expenses = exp_month['amount'].sum() if not exp_month.empty else 0
        net_savings = total_income - total_expenses

        last_updated = pd.to_datetime(exp_month['last_updated'].max()).strftime("%d-%m-%Y %H:%M") if 'last_updated' in exp_month.columns and not exp_month.empty else "No updates yet"

        # Format dashboard title with month
        if selected_month == "All Time":
            formatted_month = "All Time"
        else:
            try:
                formatted_month = pd.Period(selected_month).strftime("%b %Y")
            except:
                formatted_month = selected_month

        st.markdown(f"### Summary for {formatted_month} (Last Updated: {last_updated})")

        col1, col2, col3 = st.columns([1.5, 1.5, 1.5])
        col1.metric("Total Income", f"₹{total_income:,.2f}")
        col2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
        col3.metric("Net Savings", f"₹{net_savings:,.2f}")

        # Telegram button
        st.subheader("Send Summary to Telegram")
        if st.button("📨 Send This Summary"):
            message = get_summary_message(selected_month)
            if send_telegram_message(message):
                st.success("✅ Summary sent to Telegram!")
            else:
                st.error("❌ Failed to send message.")

        if not exp_month.empty:
            st.subheader("Expense by Category")
            fig, ax = plt.subplots()
            exp_month.groupby("category")['amount'].sum().plot.pie(autopct="%.1f%%", startangle=90, ax=ax, shadow=True)
            ax.set_ylabel("")
            st.pyplot(fig)

            st.subheader("Top 5 Expense Sub-categories")
            top5 = exp_month.groupby('sub_category')['amount'].sum().sort_values(ascending=False).head(5)
            st.bar_chart(top5)
    else:
        st.info("No data available. Add income and expenses first!")

# -------------------- ADD INCOME -------------------- #
# (UNCHANGED – your existing logic)

# -------------------- ADD EXPENSE -------------------- #
# (UNCHANGED – your existing logic)

# -------------------- VIEW DATA -------------------- #
# (UNCHANGED – your existing logic)

# -------------------- MONTHLY COMPARISON -------------------- #
# (UNCHANGED – your existing logic)

# -------------------- YEARLY COMPARISON -------------------- #
# (UNCHANGED – your existing logic)


# -------------------- ADD INCOME -------------------- #
elif page == "Add Income":
    st.header("➕ Add Income")
    source_options = ["Salary", "Bonus", "Freelance", "Other"]
    source_selection = st.selectbox("Source", source_options)
    source = st.text_input("Enter Source") if source_selection == "Other" else source_selection
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    month = st.date_input("Month").strftime("%Y-%m")
    if st.button("Save Income"):
        if not source.strip():
            st.error("Please enter a valid source!")
        elif amount <= 0:
            st.error("Amount must be greater than 0!")
        else:
            run_query("INSERT INTO income (source, amount, month) VALUES (?, ?, ?)", (source.strip(), amount, month))
            st.success(f"Income of ₹{amount:,.2f} added for {month}.")

# -------------------- ADD EXPENSE -------------------- #
elif page == "Add Expense":
    st.header("➕ Add Expense")
    category = st.selectbox("Category", main_categories)
    sub_category = st.text_input("Sub-category (Mandatory)") if category == "Misc" else st.selectbox("Sub-category", sub_categories_dict[category])

    if category == "Credit Card" and sub_category in credit_card_dates:
        statement_date = credit_card_dates[sub_category]['statement']
        payment_due = credit_card_dates[sub_category]['payment']
        st.info(f"**Statement Date:** {statement_date}  |  **Payment Due Date:** {payment_due}")

    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    date = st.date_input("Date")

    if st.button("Save Expense"):
        if category == "Misc" and not sub_category.strip():
            st.error("Sub-category is mandatory for Misc!")
        elif amount <= 0:
            st.error("Amount must be greater than 0!")
        else:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            if category == "Credit Card":
                # Check for same month and sub-category
                month_str = date.strftime("%Y-%m")
                c.execute("SELECT id FROM expenses WHERE category='Credit Card' AND sub_category=? AND strftime('%Y-%m', date)=?", (sub_category.strip(), month_str))
                existing = c.fetchone()
                if existing:
                    c.execute("UPDATE expenses SET amount=?, date=?, last_updated=datetime('now') WHERE id=?", (amount, str(date), existing[0]))
                    st.success(f"{sub_category} expense updated for {month_str} to ₹{amount:,.2f}")
                else:
                    c.execute("INSERT INTO expenses (category, sub_category, amount, date, last_updated) VALUES (?, ?, ?, ?, datetime('now'))", (category, sub_category.strip(), amount, str(date)))
                    st.success(f"{sub_category} expense of ₹{amount:,.2f} added for {month_str}")
            else:
                c.execute("INSERT INTO expenses (category, sub_category, amount, date, last_updated) VALUES (?, ?, ?, ?, datetime('now'))", (category, sub_category.strip(), amount, str(date)))
                st.success(f"Expense of ₹{amount:,.2f} added under {category}")
            conn.commit()
            conn.close()

# -------------------- VIEW DATA -------------------- #
elif page == "View Data":
    st.header("📜 Raw Data")
    exp_df = fetch_df("SELECT * FROM expenses")
    income_df = fetch_df("SELECT * FROM income")

    # Filter by month
    st.subheader("Filter by Month")
    all_months = sorted(list(set(
        pd.to_datetime(exp_df['date']).dt.to_period('M').astype(str).tolist() +
        pd.to_datetime(income_df['month']).dt.to_period('M').astype(str).tolist()
    )))
    selected_month = st.selectbox("Select Month", ["All"] + all_months)

    if selected_month != "All":
        exp_df = exp_df[pd.to_datetime(exp_df['date']).dt.to_period('M').astype(str) == selected_month]
        income_df = income_df[pd.to_datetime(income_df['month']).dt.to_period('M').astype(str) == selected_month]

    # Income Table
    st.subheader("Income")
    st.dataframe(income_df)
    if not income_df.empty:
        income_ids = st.multiselect("Select Income(s) to delete", income_df['id'])
        if st.button("Delete Selected Income(s)"):
            if income_ids:
                placeholders = ",".join("?"*len(income_ids))
                run_query(f"DELETE FROM income WHERE id IN ({placeholders})", tuple(income_ids))
                st.success(f"Deleted {len(income_ids)} income record(s).")
            else:
                st.warning("Please select at least one income record to delete.")
        st.markdown("---")
        st.subheader("Edit Income")
        edit_income_id = st.selectbox("Select Income to Edit", income_df['id'])
        if edit_income_id:
            row = income_df[income_df['id'] == edit_income_id].iloc[0]
            new_source = st.text_input("Source", row['source'])
            new_amount = st.number_input("Amount", value=row['amount'], min_value=0.0, step=0.01)
            # Fix Period to date
            if isinstance(row['month'], pd.Period):
                new_month_default = row['month'].to_timestamp().date()
            else:
                new_month_default = pd.to_datetime(row['month']).date()
            new_month = st.date_input("Month", new_month_default)
            if st.button("Update Selected Income"):
                run_query("UPDATE income SET source=?, amount=?, month=? WHERE id=?",
                          (new_source.strip(), new_amount, new_month.strftime("%Y-%m"), edit_income_id))
                st.success(f"Income ID {edit_income_id} updated successfully.")

    # Expenses Table
    st.subheader("Expenses")
    st.dataframe(exp_df)
    if not exp_df.empty:
        expense_ids = st.multiselect("Select Expense(s) to delete", exp_df['id'])
        if st.button("Delete Selected Expense(s)"):
            if expense_ids:
                placeholders = ",".join("?"*len(expense_ids))
                run_query(f"DELETE FROM expenses WHERE id IN ({placeholders})", tuple(expense_ids))
                st.success(f"Deleted {len(expense_ids)} expense record(s).")
            else:
                st.warning("Please select at least one expense record to delete.")
        st.markdown("---")
        st.subheader("Edit Expense(s)")
        selected_expenses = st.multiselect("Select Expense(s) to Edit", exp_df['id'])
        if selected_expenses:
            first_row = exp_df[exp_df['id'] == selected_expenses[0]].iloc[0]
            category_options = main_categories
            category = st.selectbox("Category", category_options, index=category_options.index(first_row['category']))
            if category == "Misc":
                sub_category = st.text_input("Sub-category", first_row['sub_category'])
            else:
                options = sub_categories_dict[category]
                idx = options.index(first_row['sub_category']) if first_row['sub_category'] in options else 0
                sub_category = st.selectbox("Sub-category", options, index=idx)
            amount = st.number_input("Amount", value=first_row['amount'], min_value=0.0, step=0.01)
            date = st.date_input("Date", pd.to_datetime(first_row['date']))
            if st.button("Update Selected Expenses"):
                for eid in selected_expenses:
                    run_query("UPDATE expenses SET category=?, sub_category=?, amount=?, date=?, last_updated=datetime('now') WHERE id=?",
                              (category, sub_category.strip(), amount, str(date), eid))
                st.success(f"Updated {len(selected_expenses)} expense record(s).")

# -------------------- MONTHLY COMPARISON -------------------- #
elif page == "Monthly Comparison":
    st.header("📊 Monthly Comparison")
    income_df = fetch_df("SELECT * FROM income")
    exp_df = fetch_df("SELECT * FROM expenses")
    if not exp_df.empty:
        exp_df['month'] = pd.to_datetime(exp_df['date']).dt.to_period('M')
    if not income_df.empty:
        income_df['month'] = pd.to_datetime(income_df['month']).dt.to_period('M')
    
    all_months = sorted(list(set(exp_df['month'].astype(str).tolist() + income_df['month'].astype(str).tolist())))
    selected_months = st.multiselect("Select Months for Comparison", all_months, default=[all_months[-1]] if all_months else [])
    
    if selected_months:
        df_comp = pd.DataFrame(index=selected_months, columns=['Income','Expenses'])
        for m in selected_months:
            df_comp.loc[m,'Income'] = income_df[income_df['month'].astype(str)==m]['amount'].sum() if not income_df.empty else 0
            df_comp.loc[m,'Expenses'] = exp_df[exp_df['month'].astype(str)==m]['amount'].sum() if not exp_df.empty else 0
        
        st.subheader("Monthly Comparison")
        fig, ax = plt.subplots(figsize=(8,5))
        df_comp.plot(kind='bar', ax=ax, color=['#1f77b4','#ff7f0e'])
        ax.set_ylabel('Amount (₹)')
        ax.set_xlabel('Month')
        ax.set_title('Income vs Expenses')
        ax.grid(axis='y')
        st.pyplot(fig)

# -------------------- YEARLY COMPARISON -------------------- #
elif page == "Yearly Comparison":
    st.header("📈 Yearly Comparison")
    income_df = fetch_df("SELECT * FROM income")
    exp_df = fetch_df("SELECT * FROM expenses")
    if not exp_df.empty:
        exp_df['year'] = pd.to_datetime(exp_df['date']).dt.year
    if not income_df.empty:
        income_df['year'] = pd.to_datetime(income_df['month']).dt.year
    
    all_years = sorted(list(set(exp_df['year'].tolist() + income_df['year'].tolist())))
    selected_years = st.multiselect("Select Years for Comparison", all_years, default=all_years)
    
    if selected_years:
        exp_year = exp_df[exp_df['year'].isin(selected_years)].groupby('year')['amount'].sum() if not exp_df.empty else pd.Series()
        income_year = income_df[income_df['year'].isin(selected_years)].groupby('year')['amount'].sum() if not income_df.empty else pd.Series()
        years = sorted(list(set(exp_year.index.tolist() + income_year.index.tolist())))
        df_year = pd.DataFrame({'Income':[income_year.get(y,0) for y in years],'Expenses':[exp_year.get(y,0) for y in years]}, index=years)
        
        st.subheader("Yearly Comparison")
        fig, ax = plt.subplots(figsize=(8,5))
        df_year.plot(kind='bar', ax=ax, color=['#1f77b4','#ff7f0e'])
        ax.set_ylabel('Amount (₹)')
        ax.set_xlabel('Year')
        ax.set_title('Income vs Expenses')
        ax.grid(axis='y')
        st.pyplot(fig)