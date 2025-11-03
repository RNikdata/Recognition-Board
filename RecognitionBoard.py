import streamlit as st
import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials
import time
import hashlib


st.set_page_config(
    page_title="Recognition Board",  # <-- Browser tab name
    page_icon="🏆",                            # <-- Favicon in browser tab
    layout="wide"                              # optional
)

# --- Google Sheets setup ---
# --- Connect to Google Sheets using Streamlit secrets ---
service_account_info = st.secrets["google_service_account"]
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(credentials)

# # Your Google Sheet ID and worksheet name
SHEET_ID = "18GgoG_BtBO10tbmNDCi2RN0MVnAjfClYhilEUnxBdIc"
EMPLOYEE_SHEET_NAME = "Employee Data"
NOMINATION_NAME = "Nomination Data"

try:
    # --- Connect to Google Sheets ---
    nomination_sheet = gc.open_by_key(SHEET_ID).worksheet(NOMINATION_NAME)
    employee_sheet = gc.open_by_key(SHEET_ID).worksheet(EMPLOYEE_SHEET_NAME)

    # --- Load data from Google Sheets ---
    df = get_as_dataframe(nomination_sheet, evaluate_formulas=True).dropna(how="all")
    df1 = get_as_dataframe(employee_sheet, evaluate_formulas=True).dropna(how="all")

    # --- Columns to bring from df1 ---
    columns_from_df1 = ["Employee Id", "Employee Name", "Manager Name", "Designation", "Account Name", "Rank"]

    # --- Merge nomination data with employee data ---
    merged_df = df.merge(df1[columns_from_df1], left_on="Employee ID", right_on="Employee Id", how="left")
    merged_df["Employee ID"] = merged_df["Employee Id"].astype(int)

    # --- Ensure approval status columns exist ---
    if "AL Approval Status" not in merged_df.columns:
        merged_df["AL Approval Status"] = "Pending"
    else:
        merged_df["AL Approval Status"] = merged_df["AL Approval Status"].fillna("Pending")

    if "BU Head Approval Status" not in merged_df.columns:
        merged_df["BU Head Approval Status"] = "Pending"
    else:
        merged_df["BU Head Approval Status"] = merged_df["BU Head Approval Status"].fillna("Pending")

except Exception as e:
    st.error(f"Error loading Google Sheets data: {e}")
    st.stop()

#######################################
# --- Page Navigation Setup ---
#######################################
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Final Display Board"

# --- Common Title & Refresh ---
header_col1, header_col2 = st.columns([6, 1])

with header_col1:
    st.markdown("<h1 style='text-align:center'>🏆 Recognition Board</h1>", unsafe_allow_html=True)

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh"):
        st.rerun()
        

# --- Top Navigation Buttons (Navbar Style) ---
nav_cols = st.columns([1,1,1,1])  # equal spacing for 4 buttons

with nav_cols[0]:
    if st.button("📝 Nomination Form", use_container_width=True):
        st.session_state["active_page"] = "Nomination Form"

with nav_cols[1]:
   if st.button("AL Selection Board", use_container_width=True):
       st.session_state["active_page"] = "AL Selection Board"

with nav_cols[2]:
   if st.button("BU Head Selection Board", use_container_width=True):
       st.session_state["active_page"] = "BU Head Selection Board"

with nav_cols[3]:
   if st.button("📊 Final Display Board", use_container_width=True):
       st.session_state["active_page"] = "Final Display Board"
st.markdown("---")

# --- Sidebar: Logo & Company Name ---
# st.sidebar.markdown(
#     """
#     <div style='text-align: left; margin-left: 43px;'>
#         <img src="https://upload.wikimedia.org/wikipedia/en/0/0c/Mu_Sigma_Logo.jpg" width="100">
#     </div>
#     """,
#     unsafe_allow_html=True
# )


# --- Tab 1: Nomination Form ---            
if st.session_state.get("active_page") == "Nomination Form":
    st.markdown( 
        "<p style='margin-top:15px; color:#b0b0b0; font-size:14px; font-style:Solid;'>" 
        'Google Form to nominate yourself for the following awards:'"</p>", 
        unsafe_allow_html=True )

    # Google Form Button
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfCvuS_dHL6cjRBwK6Qz_NsRHQXIu9jRI3SppJt3lwjhWeUCQ/viewform?usp=sharing&ouid=116479912870922545263"
    st.markdown(
        f"""
        <div style='margin-bottom:20px;'>
            <a href="{google_form_url}" target="_blank">
                <button style="
                    background-color:#4CAF50;  /* dark grey button */
                    color:white;
                    padding:12px 24px;
                    border:none;
                    border-radius:8px;
                    font-size:16px;
                    font-weight:600;
                    cursor:pointer;">
                    📝 Open Nomination Form
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Awards data
    awards = [
        {
            "title": 'Reliability – "Anchor of Trust" Award',
            "criteria": [
                "Consistency: Delivering high-quality work on time, every time.",
                "Dependability: Being a go-to person on the team for critical tasks.",
                "Quality: Maintaining a high standard of accuracy and completeness in all outputs.",
                "Others: Please mention."
            ]
        },
        {
            "title": 'Learning – "Knowledge Catalyst" Award',
            "criteria": [
                "Initiative: Proactively seeking new skills or knowledge.",
                "Application: Applying new learnings to a project or task.",
                "Knowledge Sharing: Actively helping others learn and grow.",
                "Others: Please mention."
            ]
        },
        {
            "title": 'Resourcing – "Efficiency Architect" Award',
            "criteria": [
                "Optimization: Finding innovative ways to save time, money, or effort.",
                "Planning: Demonstrating excellent foresight in resource allocation.",
                "Problem-Solving: Creatively overcoming resourcing challenges.",
                "Others: Please mention."
            ]
        },
        {
            "title": 'Growth – "Momentum Maker" Award',
            "criteria": [
                "Contribution: Directly impacting a project or business unit's growth.",
                "Scalability: Building solutions or processes that can grow with the company.",
                "Proactivity: Identifying and pursuing new opportunities.",
                "Others: Please mention."
            ]
        },
        {
            "title": 'Akasa – "Apex Innovator" Award',
            "criteria": [
                "Vision: Introducing a completely new idea, tool, or methodology.",
                "Impact: Leading to a significant breakthrough or change.",
                "Excellence: Work that stands out as a top-tier example of problem-solving.",
                "Others: Please mention."
            ]
        },
        {
            "title": 'Value/Impact – "Ripple Effect" Award',
            "criteria": [
                "Significance: Creating substantial positive outcomes for clients, projects, or teams.",
                "Influence: Inspiring or influencing others to improve their work.",
                "Tangible Results: Measurable impact through data or feedback.",
                "Others: Please mention."
            ]
        }
    ]

    # Two-column layout
    col1, col2 = st.columns(2)

    for i, award in enumerate(awards):
        html_content = f"""
        <div style='border:1px solid #555555; border-radius:8px; padding:15px; margin-bottom:15px; background: linear-gradient(135deg, #1C1C1C, #2F2F2F);
color:white;'>
            <p style='font-weight:bold; font-size:15px; margin-bottom:10px;'>{award['title']}</p>
            <ul style='margin-left:15px;'>
        """
        for crit in award['criteria']:
            html_content += f"<li>{crit}</li>"
        html_content += "</ul></div>"

        if i % 2 == 0:
            col1.markdown(html_content, unsafe_allow_html=True)
        else:
            col2.markdown(html_content, unsafe_allow_html=True)

elif st.session_state.get("active_page") == "AL Selection Board":
    # --- Sidebar Filters ---
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.header("⚙️ Filters")
    account_filter = st.sidebar.multiselect("Account Name", options=df1["Account Name"].dropna().unique())
    manager_filter = st.sidebar.multiselect("Manager Name", options=df1["Manager Name"].dropna().unique())
    designation_filter = st.sidebar.multiselect("Designation", options=df1["Designation"].dropna().unique())
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.header("🔎 Search")
    resource_search = st.sidebar.text_input("Search Employee Name or ID",placeholder = "Employe ID/Name")

    if account_filter:
        merged_df = merged_df[merged_df["Account Name"].isin(account_filter)]
    if manager_filter:
        merged_df = merged_df[merged_df["Manager Name"].isin(manager_filter)]
    if designation_filter:
        merged_df = merged_df[merged_df["Designation"].isin(designation_filter)]
    if resource_search:
        merged_df = merged_df[
            merged_df["Employee Name"].str.contains(resource_search, case=False, na=False) |
            merged_df["Employee Id"].astype(str).str.contains(resource_search, na=False)
        ]
    
    st.subheader("AL Selection Board")
    
    try:
        # Rename columns for display
        df_display = merged_df.rename(columns={
            "Which title would you like to nominate yourself for?": "Nominated Title",
            "Please state the reason for your self-nomination": "Self Nomination Reason"
        })
    
        # Function to color status
        def color_status(val):
            if val == "Approved":
                color = 'green'
            elif val == "Rejected":
                color = 'red'
            else:  # Pending
                color = 'orange'
            return f'color: {color}; font-weight:bold'
    
        # Show styled table
        st.dataframe(
            df_display[["Nomination ID", "Employee ID", "Employee Name", "Manager Name", "Designation", "Account Name", "Rank", "Nominated Title", "Self Nomination Reason", "AL Approval Status", "AL Comment"]]
            .style.applymap(color_status, subset=["AL Approval Status"]),
            use_container_width=True,hide_index = True,height = 250
        )
    
        st.markdown("---")
    
        # Dropdown to select Nomination ID
        nomination_ids = merged_df.loc[merged_df["AL Approval Status"] == "Pending", "Nomination ID"].tolist()
        selected_id = st.selectbox("Select Nomination ID to Approve/Reject:", nomination_ids)

        # Input box for AL Comments
        al_comment = st.text_area("AL Comment:", placeholder="Enter your comments here...")
        
        # Radio button for approval
        approval_choice = st.radio("Decision:", ["Approve", "Reject"], horizontal=True)
        
        # Submit button
        if st.button("Submit Decision"):
            # Update the Status for selected Nomination ID
            merged_df.loc[merged_df["Nomination ID"] == selected_id, "AL Approval Status"] = \
                "Approved" if approval_choice == "Approve" else "Rejected"
            
            # Add comments column if not exists
            if "AL Comment" not in merged_df.columns:
                merged_df["AL Comment"] = ""
        
            # Update comments for selected nomination
            merged_df.loc[merged_df["Nomination ID"] == selected_id, "AL Comment"] = al_comment
        
            # Save back to Excel (only original df columns + new comment column)
            cols_to_save = df.columns.tolist()
            set_with_dataframe(nomination_sheet, merged_df)

            # Clear the text area after submission
            st.session_state["al_comment_input"] = ""
        
            st.success(f"Nomination ID {selected_id} has been {approval_choice}d successfully!")
            time.sleep(2)
            st.rerun()

    except Exception as e:
        st.error(f"Error loading Excel: {e}")

elif st.session_state.get("active_page") == "BU Head Selection Board":
    # --- Sidebar Filters ---
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.header("⚙️ Filters")
    account_filter = st.sidebar.multiselect("Account Name", options=df1["Account Name"].dropna().unique())
    manager_filter = st.sidebar.multiselect("Manager Name", options=df1["Manager Name"].dropna().unique())
    designation_filter = st.sidebar.multiselect("Designation", options=df1["Designation"].dropna().unique())
    st.sidebar.markdown("<br><br>",unsafe_allow_html = True)
    st.sidebar.header("🔎 Search")
    resource_search = st.sidebar.text_input("Search Employee Name or ID",placeholder = "Employe ID/Name")

    if account_filter:
        merged_df = merged_df[merged_df["Account Name"].isin(account_filter)]
    if manager_filter:
        merged_df = merged_df[merged_df["Manager Name"].isin(manager_filter)]
    if designation_filter:
        merged_df = merged_df[merged_df["Designation"].isin(designation_filter)]
    if resource_search:
        merged_df = merged_df[
            merged_df["Employee Name"].str.contains(resource_search, case=False, na=False) |
            merged_df["Employee Id"].astype(str).str.contains(resource_search, na=False)
        ]
    
    st.subheader("BU Head Selection Board")

    try:
        # Rename columns for display
        df_display = merged_df.rename(columns={
            "Which title would you like to nominate yourself for?": "Nominated Title",
            "Please state the reason for your self-nomination": "Self Nomination Reason"
        })

        # Function to color status
        def color_status(val):
            if val == "Approved":
                color = 'green'
            elif val == "Rejected":
                color = 'red'
            else:  # Pending
                color = 'orange'
            return f'color: {color}; font-weight:bold'

        # Filter to show only nominations approved by AL
        df_display_filtered = df_display[df_display["AL Approval Status"] == "Approved"]
        # Ensure Rank is integer for display
        df_display_filtered["BU Head Rank"] = df_display["BU Head Rank"].astype("Int64")
        # Show styled table
        st.dataframe(
            df_display_filtered[["Nomination ID", "Employee ID", "Employee Name","Manager Name", "Designation", "Account Name", "Rank", "Nominated Title", "Self Nomination Reason", "AL Approval Status", "AL Comment", "BU Head Approval Status", "BU Head Comment","BU Head Rank"]]
            .style.applymap(color_status, subset=["AL Approval Status", "BU Head Approval Status"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Dropdown: Nomination IDs where AL approved & BU Head pending
        nomination_ids = merged_df.loc[
            (merged_df["AL Approval Status"] == "Approved") &
            (merged_df["BU Head Approval Status"] == "Pending"),
            "Nomination ID"
        ].tolist()

        if nomination_ids:
            # Two columns for dropdown and rank input
            col1, col2 = st.columns([2, 1])
        
            with col1:
                selected_id = st.selectbox("Select Nomination ID to Approve/Reject:", nomination_ids)
        
            with col2:
                bu_rank = st.text_input(
                    "Rank:", 
                    placeholder="Enter Rank", 
                    key="bu_rank_input"
                )
        
            # Text area for BU Head comments below
            bu_comment = st.text_area(
                "BU Head Comments:", 
                placeholder="Enter your comments here...", 
                key="bu_comment_input"
            )
        
            # Radio button for approval
            approval_choice = st.radio("Decision:", ["Approve", "Reject"], horizontal=True)
        
            # Submit button
            if st.button("Submit Decision"):
                # Update BU Head Approval Status
                merged_df.loc[merged_df["Nomination ID"] == selected_id, "BU Head Approval Status"] = \
                    "Approved" if approval_choice == "Approve" else "Rejected"
        
                # Add BU Head Comment column if it doesn't exist
                if "BU Head Comment" not in merged_df.columns:
                    merged_df["BU Head Comment"] = ""
        
                # Save comment
                merged_df.loc[merged_df["Nomination ID"] == selected_id, "BU Head Comment"] = bu_comment
        
                # Save Rank
                merged_df.loc[merged_df["Nomination ID"] == selected_id, "BU Head Rank"] = bu_rank
        
                # Save only original df columns
                set_with_dataframe(nomination_sheet, merged_df)
        
                st.success(f"Nomination ID {selected_id} has been {approval_choice}d successfully!")
                time.sleep(2)
                st.rerun()


        else:
            st.info("No nominations pending for BU Head approval.")

    except Exception as e:
        st.error(f"Error loading Excel: {e}")
    
elif st.session_state.get("active_page") == "Final Display Board":
    
    award_list_col1 = [
        "Award 1",
        "Award 2",
        "Anchor of Trust Award",
        "Knowledge Catalyst Award",
        "Efficiency Architect Award",
        "Momentum Maker Award",
        "Apex Innovator Award",
        "Ripple Effect Award"]
    
    # Fixed box style
    box_style = """
    <div style="
        width: 300px;
        height: 180px;
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 0;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin: 0;             /* no extra margin */
    ">
        <div style="font-weight:bold; font-size:16px; margin-bottom:10px;">Award Name</div>
        <div style="font-size:14px;">Winner Name</div>
    </div>
    """
    
    box_style1 = """
    <div style="
        width: 300px;
        height: 375px;
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 0;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin: 0;             /* removed auto */
    ">
        <div style="font-weight:bold; font-size:16px; margin-bottom:10px;">Award Name</div>
        <div style="font-size:14px;">Winner Name</div>
    </div>
    """
    box_style2 = """
    <div style="
        width: 1295px;
        height: 250px;
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 0;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin: 0;             /* removed auto */
    ">
        <div style="font-weight:bold; font-size:16px; margin-bottom:10px;">Award Name</div>
        <div style="font-size:14px;">Winner Name</div>
    </div>
    """
    box_style3 = """
    <div style="
        width: 300px;
        height: 250px;
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 0;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin: 0;             /* removed auto */
    ">
        <div style="font-weight:bold; font-size:16px; margin-bottom:10px;">Award Name</div>
        <div style="font-size:14px;">Winner Name</div>
    </div>
    """
    def get_box_html1(award_name, winner_name, winner_id, photo_url, rising_stars, width, height):
        # Build Rising Stars HTML
        rising_html = ""
        if rising_stars:
            rising_html += "<div style='display:flex; flex-direction:column; gap:4px;'>"
            for name in rising_stars:
                rising_html += f"<div style='font-size:14px; color:white; text-align:left;'>{name}</div>"
            rising_html += "</div>"
        else:
            rising_html = "<div style='font-size:14px; color:#ccc;'>No Rising Stars</div>"
    
        return f"""
        <div style="
        width: auto;
        height: {height}px;
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 10px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin: 5px 0;
        ">
        <!-- Award Title -->
        <div style='font-weight:bold; font-size:18px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
            🏆 {award_name}
        </div>
    
        <!-- Two columns inside card -->
        <div style="display:flex; gap:15px;">

        <!-- Winner Column -->
        <div style="flex:1; display:flex; flex-direction:column; align-items:flex-start; text-align:left;">
            <br>
            <img src='{photo_url}' style='width:60px; height:60px; border-radius:50%; object-fit:cover; border:2px solid #fff; margin-bottom:5px;'>
            <div style='font-size:14px; font-weight:bold; color:#FFD700;'>{winner_name}</div>
            <div style='font-size:14px; color:#ccc;'>{winner_id}</div>
        </div>
    
        <!-- Rising Stars Column -->
        <div style="flex:1;">
        <br>
        <div style='font-weight:bold; font-size:18px; margin-bottom:5px; color:#1ABC9C;'>Rising Stars</div>
            {rising_html}
        </div>

        </div>
        </div>
        """

    def get_box_html(award_name, winner_name, winner_id, photo_url, width, height):
        return f"""
        <div style="
            width: {width}px;
            height: {height}px;
            background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 10px;
            color: white;
            display: flex;
            flex-direction: column;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            margin: 5px 0;
        ">
            <div style='font-weight:bold;justify-content: flex-start; font-size:16px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block;text-align:left;'>
                🏆 {award_name}
            </div>
            <div style='text-align:center; justify-content: center; margin-bottom:5px;'>
            <img src='{photo_url}' 
                 style='width:60px; height:60px; border-radius:50%; object-fit:cover; border:2px solid #fff;'>
            </div>
            <div style='font-size:14px;'>{winner_name}</div>
            <div style='font-size:12px; color:#ccc;'>{winner_id}</div>
        </div>
        """
    def get_box_html_impact_multiple(award_name, winners, width, height):
        """
        winners: list of dicts with keys 'name', 'id', 'photo'
        """
        # If winners list is empty, show "No Winners"
        if not winners:
            winners_html = "<div style='display:flex; justify-content:center; align-items:center; font-size:22px; color:#ccc; text-align:center; width:100%;height:100%;'>No Winners</div>"
            html = f"""
            <div style="width: {width}px; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:flex; gap:10px; justify-content:center; align-items:start; overflow-y:auto;'>
                    {winners_html}
                </div>
            </div>
            """
        else:
            winners_html = ""
            for w in winners:
                winners_html += "<div style='display:flex; flex-direction:column; align-items:center; justify-content:center; margin:5px;'>"
                if w.get('photo', "") != "":
                    winners_html += f"<img src='{w['photo']}' style='width:80px; height:80px; border-radius:50%; object-fit:cover; border:2px solid #fff; margin-bottom:5px;'>"
                winners_html += f"<div style='font-size:12px; font-weight:bold; text-align:center;'>{w['name']}</div>"
                winners_html += f"<div style='font-size:11px; color:#ccc; text-align:center;'>{w['id']}</div>"
                winners_html += "</div>"
    
            html = f"""
            <div style="width: {width}px; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; justify-content:center; align-items:start; overflow-y:auto;'>
                    {winners_html}
                </div>
            </div>
            """
        return html

    def get_box_html_spot_multiple(award_name, winners, width, height):
        """
        winners: list of dicts with keys 'name', 'id', 'photo'
        """
        # If winners list is empty, show "No Winners"
        if not winners:
            winners_html = "<div style='display:flex; justify-content:center; align-items:center; font-size:22px; color:#ccc; text-align:center; width:100%;height:100%;'>No Winners</div>"
            html = f"""
            <div style="width: {width}px; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:flex; gap:10px; justify-content:center; align-items:start; overflow-y:auto;'>
                    {winners_html}
                </div>
            </div>
            """
        else:
            winners_html = ""
            for w in winners:
                winners_html += "<div style='display:flex; flex-direction:column; align-items:center; justify-content:center; margin:5px;'>"
                if w.get('photo', "") != "":
                    winners_html += f"<img src='{w['photo']}' style='width:80px; height:80px; border-radius:50%; object-fit:cover; border:2px solid #fff; margin-bottom:5px;'>"
                winners_html += f"<div style='font-size:12px; font-weight:bold; text-align:center;'>{w['name']}</div>"
                winners_html += f"<div style='font-size:11px; color:#ccc; text-align:center;'>{w['id']}</div>"
                winners_html += "</div>"
    
            html = f"""
            <div style="width: {width}px; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; justify-content:center; align-items:start; overflow-y:auto;'>
                    {winners_html}
                </div>
            </div>
            """
        return html

    def get_box_html_sm_multiple(award_name, winners, height):
        """
        winners: list of dicts with keys 'name', 'id', 'photo'
        """
        # If winners list is empty, show "No Winners"
        if not winners:
            winners_html = "<div style='display:flex; justify-content:center; align-items:center; font-size:22px; color:#ccc; text-align:center; width:100%;height:100%;'>No Winners</div>"
            html = f"""
            <div style="width: auto; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:flex; gap:10px; justify-content:center; align-items:start; overflow-y:auto;'>
                    {winners_html}
                </div>
            </div>
            """
        else:
            winners_html = ""
            for w in winners:
                winners_html += "<div style='flex:0 0 auto;display:flex; flex-direction:column; align-items:center; justify-content:center; margin:5px;'>"
                if w.get('photo', "") != "":
                    winners_html += f"<img src='{w['photo']}' style='width:80px; height:80px; border-radius:50%; object-fit:cover; border:2px solid #fff; margin-bottom:5px;'>"
                winners_html += f"<div style='font-size:12px; font-weight:bold; text-align:center;'>{w['name']}</div>"
                winners_html += f"<div style='font-size:11px; color:#ccc; text-align:center;'>{w['id']}</div>"
                winners_html += "</div>"
    
            html = f"""
            <div style="width: 100%; height: {height}px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(6px); border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px; padding: 10px; color: white; display: flex; flex-direction: column;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin: 5px 0;">
                <!-- Award Name -->
                <div style='font-weight:bold; font-size:20px; margin-bottom:10px; background:#FFD70033; color:#FFD700; padding:4px 8px; border-radius:6px; display:inline-block; text-align:left;'>
                    🏆 {award_name}
                </div>
                <!-- Winners section in 2 columns -->
                <div style='flex:1; display:flex;flex-direction:row; gap:100px; justify-content:flex-start; align-items:center; overflow-x:auto; white-space:nowrap;'>
                    {winners_html}
                </div>
            </div>
            """
        return html


    col1, col2 = st.columns([4, 1])
       
    with col1:
        # First two rows with 4 boxes each
        total_boxes = 8
        cols_per_row = 4
        
        for i,names in enumerate(award_list_col1):
            if i % cols_per_row == 0:
                cols = st.columns(cols_per_row)

            award_df = merged_df[
                (merged_df["Which title would you like to nominate yourself for?"] == names) &
                (merged_df["BU Head Approval Status"] == "Approved")
            ].copy()

            width = 290
            height = 230

            if award_df.empty:
                winner_name = "No Winner"
                winner_id = "00000"
                photo_url = "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"
            else:
                winner = award_df[award_df["BU Head Rank"] == 1]
                if not winner.empty:
                    w = winner.iloc[0]
                    winner_name = w["Employee Name"]
                    winner_id = w["Employee ID"]
                    photo_url = "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"
                else:
                    winner_name = "No Winner"
                    winner_id = "00000"
                    photo_url = "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"

            rising_stars_df = award_df[(award_df["BU Head Rank"] > 1) & (award_df["BU Head Rank"] <= 5)]
            rising_stars = rising_stars_df["Employee Name"].tolist()

            # Generate HTML for box
            box_html = get_box_html1(names, winner_name, winner_id, photo_url,rising_stars, width, height)
            with cols[i % cols_per_row]:
                st.markdown(box_html, unsafe_allow_html=True)
            
            # Spacer after each row
            if (i + 1) % cols_per_row == 0:
                st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
        
        # Third row with a single box
        award_df = merged_df[
                (merged_df["Which title would you like to nominate yourself for?"] == "Special Mentions") &
                (merged_df["BU Head Approval Status"] == "Approved")
            ].copy()

        winners_list = []

        if not award_df.empty:
            for _, row in award_df.iterrows():
                winners_list.append({
                    "name": row["Employee Name"],
                    "id": row["Employee ID"],
                    "photo": "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"
                })

        box_html0 = get_box_html_sm_multiple("Special Mentions", winners_list,height=220)
        st.markdown(box_html0, unsafe_allow_html=True)

    with col2:
        award_df = merged_df[
            (merged_df["Which title would you like to nominate yourself for?"] == "Spot Award") &
            (merged_df["BU Head Approval Status"] == "Approved")
        ].copy()
    
        winners_list = []
    
        if not award_df.empty:
            for _, row in award_df.iterrows():
                winners_list.append({
                    "name": row["Employee Name"],
                    "id": row["Employee ID"],
                    "photo": "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"
                })

        box_html2 = get_box_html_spot_multiple("Spot Award", winners_list, width=290, height=350)
        st.markdown(box_html2, unsafe_allow_html=True)
        st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
        # Second row box (smaller)
        award_df = merged_df[
                (merged_df["Which title would you like to nominate yourself for?"] == "Impact Award") &
                (merged_df["BU Head Approval Status"] == "Approved")
            ].copy()
        winners_list = []
    
        if not award_df.empty:
            for _, row in award_df.iterrows():
                winners_list.append({
                    "name": row["Employee Name"],
                    "id": row["Employee ID"],
                    "photo": "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"
                })

        box_html3 = get_box_html_impact_multiple("Impact Award", winners_list, width=290, height=355)
        st.markdown(box_html3, unsafe_allow_html=True)
        st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
