import streamlit as st
import datetime
from db_operations import (
    add_task,
    add_user,
    add_company,
    add_contact,
    add_product
)
from db_queries import (
    get_all_companies_summary,
    get_tasks_by_company_name
)
from db_export import (
    export_tasks_csv,
    export_master_data_csv
)

st.set_page_config(page_title="Mobilint CRM", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Data"])

if page == "Dashboard":
    st.title("Dashboard & Export")
    # --- Company Summary ---
    st.subheader("Company Summary")
    companies = get_all_companies_summary()
    st.dataframe(companies)
    if st.button("Export Company Summary"):
        csv = export_master_data_csv("companies")
        st.download_button("Download Companies CSV", csv, "companies.csv", "text/csv")
    
    # --- Recent Tasks ---
    st.subheader("Recent Tasks")
    company_names = [c["company_name"] for c in companies]
    recent_company = st.selectbox("Select Company", company_names)
    if recent_company:
        tasks = get_tasks_by_company_name(recent_company)
        st.dataframe(tasks)
        if st.button("Export Tasks for " + recent_company):
            csv = export_tasks_csv(recent_company)
            st.download_button("Download Tasks CSV", csv, "tasks.csv", "text/csv")

else:
    st.title("Add Data")
    add_type = st.selectbox("Choose Data to Add", ["Task", "User", "Company", "Contact", "Product"])

    # --- Add Task Form ---
    if add_type == "Task":
        with st.form("task_form"):
            user_id      = st.selectbox("Assigned User ID", [1,2,3], index=0)
            company_name = st.text_input("Company Name")
            contact_name = st.text_input("Contact Name (optional)")
            action_date  = st.date_input("Action Date", datetime.date.today())
            task_type    = st.selectbox("Task Type", ['meeting','contact','quote','trial','tech_inquiry','delayed'])
            agenda       = st.text_area("Agenda / Summary")
            action_item  = st.text_area("Action Item / Next Step")
            due_date     = st.date_input("Due Date (optional)", value=None)
            submitted = st.form_submit_button("Create Task")
            if submitted:
                new_id = add_task(
                    user_id=user_id,
                    company_name=company_name.strip(),
                    action_date=action_date.strftime("%Y-%m-%d"),
                    contact_name=contact_name.strip(),
                    agenda=agenda.strip(),
                    action_item=action_item.strip(),
                    due_date=(due_date.strftime("%Y-%m-%d") if due_date else None),
                    project_id=None
                )
                if new_id:
                    st.success(f"New Task created (ID: {new_id})")
                else:
                    st.error("Failed to create Task. Check inputs and retry.")

    # --- Add Master Data Forms ---
    elif add_type == "User":
        with st.form("user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email    = st.text_input("Email")
            submitted = st.form_submit_button("Create User")
            if submitted:
                uid = add_user(username=username.strip(), password=password, email=email.strip())
                if uid:
                    st.success(f"User created (ID: {uid})")
                else:
                    st.error("Failed to create user.")

    elif add_type == "Company":
        with st.form("company_form"):
            name        = st.text_input("Company Name")
            count       = st.number_input("Employee Count", min_value=0)
            revenue     = st.number_input("Revenue", min_value=0)
            overview    = st.text_area("Overview")
            website     = st.text_input("Website URL")
            nationality = st.text_input("Nationality Code (alpha-3)")
            submitted = st.form_submit_button("Create Company")
            if submitted:
                cid = add_company(
                    company_name=name.strip(),
                    employee_count=count,
                    revenue=revenue,
                    overview=overview.strip(),
                    website=website.strip(),
                    nationality=nationality.strip()
                )
                if cid:
                    st.success(f"Company created (ID: {cid})")
                else:
                    st.error("Failed to create company.")

    elif add_type == "Contact":
        with st.form("contact_form"):
            company_id  = st.number_input("Company ID", min_value=1)
            name        = st.text_input("Contact Name")
            department  = st.text_input("Department")
            position    = st.text_input("Position")
            email       = st.text_input("Email")
            phone       = st.text_input("Phone")
            mobile      = st.text_input("Mobile Phone")
            submitted = st.form_submit_button("Create Contact")
            if submitted:
                cid = add_contact(
                    company_id=company_id,
                    contact_name=name.strip(),
                    department=department.strip(),
                    position=position.strip(),
                    email=email.strip(),
                    phone=phone.strip(),
                    mobile_phone=mobile.strip()
                )
                if cid:
                    st.success(f"Contact created (ID: {cid})")
                else:
                    st.error("Failed to create contact.")

    elif add_type == "Product":
        with st.form("product_form"):
            name     = st.text_input("Product Name")
            min_price= st.number_input("Min Price", min_value=0.0, format="%.2f")
            max_price= st.number_input("Max Price", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Create Product")
            if submitted:
                pid = add_product(
                    product_name=name.strip(),
                    min_price=min_price,
                    max_price=max_price
                )
                if pid:
                    st.success(f"Product created (ID: {pid})")
                else:
                    st.error("Failed to create product.")

