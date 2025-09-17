import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.captcha = None
    st.session_state.login_attempts = 0

# Sample data initialization
if 'attendance_data' not in st.session_state:
    # Generate sample attendance data
    students = [f"STU{i:03d}" for i in range(1, 21)]
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    attendance_records = []
    for student in students:
        for date in dates:
            if date.weekday() < 5:  # Only weekdays
                attendance_records.append({
                    'student_id': student,
                    'date': date.strftime('%Y-%m-%d'),
                    'status': random.choice(['Present', 'Present', 'Present', 'Absent']),
                    'class': f"Class {random.choice(['A', 'B', 'C'])}"
                })
    
    st.session_state.attendance_data = pd.DataFrame(attendance_records)

if 'leave_applications' not in st.session_state:
    st.session_state.leave_applications = pd.DataFrame(columns=[
        'application_id', 'student_id', 'from_date', 'to_date', 
        'reason', 'status', 'applied_to', 'applied_date'
    ])

# User credentials (in production, use proper database and hashing)
USERS = {
    'admin001': {'password': hashlib.md5('admin123'.encode()).hexdigest(), 'type': 'admin', 'name': 'Admin User'},
    'FAC001': {'password': hashlib.md5('faculty123'.encode()).hexdigest(), 'type': 'faculty', 'name': 'Dr. Smith'},
    'FAC002': {'password': hashlib.md5('faculty123'.encode()).hexdigest(), 'type': 'faculty', 'name': 'Prof. Johnson'},
    'STU001': {'password': hashlib.md5('student123'.encode()).hexdigest(), 'type': 'student', 'name': 'John Doe'},
    'STU002': {'password': hashlib.md5('student123'.encode()).hexdigest(), 'type': 'student', 'name': 'Jane Smith'},
    'STU003': {'password': hashlib.md5('student123'.encode()).hexdigest(), 'type': 'student', 'name': 'Bob Wilson'},
}

def generate_captcha():
    """Generate a random CAPTCHA string"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def verify_captcha(input_captcha, actual_captcha):
    """Verify if the entered CAPTCHA is correct"""
    return input_captcha.upper() == actual_captcha

def authenticate_user(username, password):
    """Authenticate user credentials"""
    if username in USERS:
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if USERS[username]['password'] == hashed_password:
            return True, USERS[username]['type'], USERS[username]['name']
    return False, None, None

def calculate_attendance_percentage(student_id):
    """Calculate attendance percentage for a student"""
    student_data = st.session_state.attendance_data[
        st.session_state.attendance_data['student_id'] == student_id
    ]
    if len(student_data) == 0:
        return 0
    present_days = len(student_data[student_data['status'] == 'Present'])
    total_days = len(student_data)
    return (present_days / total_days) * 100

def login_page():
    """Display the login page"""
    # Custom CSS for blue background and white login box
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .login-box {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: auto;
        }
        .captcha-box {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 24px;
            letter-spacing: 5px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("# 🎓 Attendance System")
        st.markdown("### Please Login")
        
        # Generate CAPTCHA if not exists
        if st.session_state.captcha is None:
            st.session_state.captcha = generate_captcha()
        
        with st.form("login_form"):
            username = st.text_input("Login ID", placeholder="Enter your ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            # Display CAPTCHA
            st.markdown("### Security Check")
            st.markdown(f'<div class="captcha-box">{st.session_state.captcha}</div>', 
                       unsafe_allow_html=True)
            captcha_input = st.text_input("Enter CAPTCHA", placeholder="Enter the code above")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_button = st.form_submit_button("🔐 Login", use_container_width=True)
            with col_btn2:
                if st.form_submit_button("🔄 Refresh CAPTCHA", use_container_width=True):
                    st.session_state.captcha = generate_captcha()
                    st.rerun()
            
            if login_button:
                if not verify_captcha(captcha_input, st.session_state.captcha):
                    st.error("❌ Invalid CAPTCHA! Please try again.")
                    st.session_state.captcha = generate_captcha()
                    st.session_state.login_attempts += 1
                    
                    if st.session_state.login_attempts >= 3:
                        st.warning("⚠️ Too many failed attempts. Please wait before trying again.")
                else:
                    success, user_type, name = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_type = user_type
                        st.session_state.user_id = username
                        st.session_state.user_name = name
                        st.success(f"✅ Welcome, {name}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                        st.session_state.captcha = generate_captcha()
        
        # Display demo credentials
        with st.expander("📋 Demo Credentials"):
            st.markdown("""
            **Admin:** admin001 / admin123  
            **Faculty:** FAC001 / faculty123  
            **Student:** STU001 / student123
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

def admin_dashboard():
    """Display admin dashboard"""
    st.title(f"👨‍💼 Admin Dashboard - Welcome, {st.session_state.user_name}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "✏️ Manage Attendance", 
                                       "📝 Leave Applications", "📈 Reports"])
    
    with tab1:
        st.header("System Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total_students = len(st.session_state.attendance_data['student_id'].unique())
        total_classes = len(st.session_state.attendance_data['class'].unique())
        avg_attendance = st.session_state.attendance_data[
            st.session_state.attendance_data['status'] == 'Present'
        ].shape[0] / st.session_state.attendance_data.shape[0] * 100
        pending_leaves = len(st.session_state.leave_applications[
            st.session_state.leave_applications['status'] == 'Pending'
        ])
        
        with col1:
            st.metric("Total Students", total_students)
        with col2:
            st.metric("Total Classes", total_classes)
        with col3:
            st.metric("Avg Attendance", f"{avg_attendance:.1f}%")
        with col4:
            st.metric("Pending Leaves", pending_leaves)
        
        # Attendance trend chart
        st.subheader("Attendance Trend")
        daily_attendance = st.session_state.attendance_data.groupby('date').apply(
            lambda x: (x['status'] == 'Present').sum() / len(x) * 100
        ).reset_index()
        daily_attendance.columns = ['Date', 'Attendance %']
        
        fig = px.line(daily_attendance, x='Date', y='Attendance %', 
                     title="Daily Attendance Percentage")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Manage Student Attendance")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_student = st.selectbox("Select Student", 
                                           st.session_state.attendance_data['student_id'].unique())
            selected_date = st.date_input("Select Date", datetime.now())
            selected_class = st.selectbox("Select Class", ['Class A', 'Class B', 'Class C'])
        
        with col2:
            st.subheader(f"Attendance Record for {selected_student}")
            student_data = st.session_state.attendance_data[
                st.session_state.attendance_data['student_id'] == selected_student
            ].copy()
            
            if not student_data.empty:
                student_data['date'] = pd.to_datetime(student_data['date'])
                student_data = student_data.sort_values('date', ascending=False).head(10)
                
                # Display editable dataframe
                edited_df = st.data_editor(
                    student_data[['date', 'status', 'class']],
                    hide_index=True,
                    column_config={
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Present", "Absent"],
                            required=True
                        )
                    }
                )
                
                col_save, col_mark = st.columns(2)
                with col_save:
                    if st.button("💾 Save Changes", use_container_width=True):
                        # Update the attendance data
                        for idx, row in edited_df.iterrows():
                            mask = (st.session_state.attendance_data['student_id'] == selected_student) & \
                                   (st.session_state.attendance_data['date'] == row['date'].strftime('%Y-%m-%d'))
                            st.session_state.attendance_data.loc[mask, 'status'] = row['status']
                        st.success("✅ Attendance updated successfully!")
                        st.rerun()
                
                with col_mark:
                    new_status = st.selectbox("Mark as", ["Present", "Absent"])
                    if st.button(f"✏️ Mark {new_status} for {selected_date}", use_container_width=True):
                        new_record = {
                            'student_id': selected_student,
                            'date': selected_date.strftime('%Y-%m-%d'),
                            'status': new_status,
                            'class': selected_class
                        }
                        st.session_state.attendance_data = pd.concat([
                            st.session_state.attendance_data,
                            pd.DataFrame([new_record])
                        ], ignore_index=True)
                        st.success(f"✅ Marked {selected_student} as {new_status}")
                        st.rerun()
    
    with tab3:
        st.header("Leave Applications")
        
        if not st.session_state.leave_applications.empty:
            pending_leaves = st.session_state.leave_applications[
                st.session_state.leave_applications['status'] == 'Pending'
            ]
            
            if not pending_leaves.empty:
                st.subheader("Pending Applications")
                for idx, leave in pending_leaves.iterrows():
                    with st.expander(f"Application from {leave['student_id']} - {leave['applied_date']}"):
                        st.write(f"**From:** {leave['from_date']} **To:** {leave['to_date']}")
                        st.write(f"**Reason:** {leave['reason']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"✅ Approve", key=f"approve_{idx}"):
                                st.session_state.leave_applications.loc[idx, 'status'] = 'Approved'
                                st.success("Leave approved!")
                                st.rerun()
                        with col2:
                            if st.button(f"❌ Reject", key=f"reject_{idx}"):
                                st.session_state.leave_applications.loc[idx, 'status'] = 'Rejected'
                                st.error("Leave rejected!")
                                st.rerun()
            else:
                st.info("No pending leave applications")
        else:
            st.info("No leave applications yet")
    
    with tab4:
        st.header("Class-wise Attendance Report")
        
        selected_class = st.selectbox("Select Class", 
                                     st.session_state.attendance_data['class'].unique())
        
        class_data = st.session_state.attendance_data[
            st.session_state.attendance_data['class'] == selected_class
        ]
        
        # Calculate attendance percentage by student
        student_attendance = class_data.groupby('student_id').apply(
            lambda x: (x['status'] == 'Present').sum() / len(x) * 100
        ).reset_index()
        student_attendance.columns = ['Student ID', 'Attendance %']
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(x=student_attendance['Student ID'], 
                   y=student_attendance['Attendance %'],
                   marker_color=['red' if x < 75 else 'green' 
                                for x in student_attendance['Attendance %']])
        ])
        fig.update_layout(title=f"Attendance Report - {selected_class}",
                         xaxis_title="Student ID", yaxis_title="Attendance %")
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed table
        st.subheader("Detailed Report")
        st.dataframe(student_attendance, use_container_width=True)

def faculty_dashboard():
    """Display faculty dashboard"""
    st.title(f"👨‍🏫 Faculty Dashboard - Welcome, {st.session_state.user_name}")
    
    tab1, tab2, tab3 = st.tabs(["📊 Student Attendance", "📝 Leave Applications", "📈 Reports"])
    
    with tab1:
        st.header("View Student Attendance")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_class = st.selectbox("Select Class", 
                                         st.session_state.attendance_data['class'].unique())
        with col2:
            date_range = st.date_input("Select Date Range", 
                                       value=(datetime.now() - timedelta(days=30), datetime.now()),
                                       key="faculty_date_range")
        
        # Display attendance data
        filtered_data = st.session_state.attendance_data[
            st.session_state.attendance_data['class'] == selected_class
        ]
        
        if len(date_range) == 2:
            filtered_data = filtered_data[
                (pd.to_datetime(filtered_data['date']) >= pd.to_datetime(date_range[0])) &
                (pd.to_datetime(filtered_data['date']) <= pd.to_datetime(date_range[1]))
            ]
        
        # Summary statistics
        st.subheader("Attendance Summary")
        col1, col2, col3 = st.columns(3)
        
        total_students = len(filtered_data['student_id'].unique())
        avg_attendance = (filtered_data['status'] == 'Present').sum() / len(filtered_data) * 100
        
        with col1:
            st.metric("Total Students", total_students)
        with col2:
            st.metric("Average Attendance", f"{avg_attendance:.1f}%")
        with col3:
            below_75 = sum([calculate_attendance_percentage(sid) < 75 
                           for sid in filtered_data['student_id'].unique()])
            st.metric("Students Below 75%", below_75)
        
        # Detailed attendance table
        st.subheader("Student-wise Attendance")
        student_summary = []
        for student in filtered_data['student_id'].unique():
            student_data = filtered_data[filtered_data['student_id'] == student]
            present = (student_data['status'] == 'Present').sum()
            total = len(student_data)
            percentage = (present / total * 100) if total > 0 else 0
            
            student_summary.append({
                'Student ID': student,
                'Present': present,
                'Absent': total - present,
                'Total Classes': total,
                'Attendance %': f"{percentage:.1f}%",
                'Status': '⚠️ Low' if percentage < 75 else '✅ Good'
            })
        
        summary_df = pd.DataFrame(student_summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.header("Leave Applications")
        
        # Display leave applications assigned to this faculty
        faculty_leaves = st.session_state.leave_applications[
            st.session_state.leave_applications['applied_to'].str.contains(
                st.session_state.user_id, na=False
            )
        ]
        
        if not faculty_leaves.empty:
            pending = faculty_leaves[faculty_leaves['status'] == 'Pending']
            
            if not pending.empty:
                st.subheader("Pending Applications")
                for idx, leave in pending.iterrows():
                    with st.expander(f"From {leave['student_id']} - {leave['applied_date']}"):
                        st.write(f"**Duration:** {leave['from_date']} to {leave['to_date']}")
                        st.write(f"**Reason:** {leave['reason']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Approve", key=f"fac_approve_{idx}"):
                                st.session_state.leave_applications.loc[idx, 'status'] = 'Approved'
                                st.success("Leave approved!")
                                st.rerun()
                        with col2:
                            if st.button(f"❌ Reject", key=f"fac_reject_{idx}"):
                                st.session_state.leave_applications.loc[idx, 'status'] = 'Rejected'
                                st.error("Leave rejected!")
                                st.rerun()
            else:
                st.info("No pending leave applications")
            
            # Show processed applications
            processed = faculty_leaves[faculty_leaves['status'] != 'Pending']
            if not processed.empty:
                st.subheader("Processed Applications")
                st.dataframe(processed[['student_id', 'from_date', 'to_date', 'status', 'applied_date']], 
                           use_container_width=True, hide_index=True)
        else:
            st.info("No leave applications assigned to you")
    
    with tab3:
        st.header("Class Reports")
        
        # Attendance trend
        st.subheader("Attendance Trends")
        class_options = st.multiselect("Select Classes", 
                                       st.session_state.attendance_data['class'].unique(),
                                       default=st.session_state.attendance_data['class'].unique()[0])
        
        if class_options:
            trend_data = []
            for class_name in class_options:
                class_data = st.session_state.attendance_data[
                    st.session_state.attendance_data['class'] == class_name
                ]
                daily = class_data.groupby('date').apply(
                    lambda x: (x['status'] == 'Present').sum() / len(x) * 100
                ).reset_index()
                daily.columns = ['Date', 'Attendance %']
                daily['Class'] = class_name
                trend_data.append(daily)
            
            if trend_data:
                combined_trend = pd.concat(trend_data)
                fig = px.line(combined_trend, x='Date', y='Attendance %', 
                            color='Class', title="Class-wise Attendance Trends")
                st.plotly_chart(fig, use_container_width=True)

def student_dashboard():
    """Display student dashboard"""
    st.title(f"👨‍🎓 Student Dashboard - Welcome, {st.session_state.user_name}")
    
    tab1, tab2, tab3 = st.tabs(["📊 My Attendance", "📝 Apply for Leave", "📋 Leave Status"])
    
    with tab1:
        st.header("My Attendance Overview")
        
        # Get student's attendance data
        my_attendance = st.session_state.attendance_data[
            st.session_state.attendance_data['student_id'] == st.session_state.user_id
        ].copy()
        
        if not my_attendance.empty:
            # Calculate statistics
            total_classes = len(my_attendance)
            present_days = len(my_attendance[my_attendance['status'] == 'Present'])
            absent_days = total_classes - present_days
            attendance_percentage = (present_days / total_classes) * 100
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Classes", total_classes)
            with col2:
                st.metric("Present", present_days)
            with col3:
                st.metric("Absent", absent_days)
            with col4:
                color = "🟢" if attendance_percentage >= 75 else "🔴"
                st.metric(f"{color} Attendance %", f"{attendance_percentage:.1f}%")
            
            # Warning if below 75%
            if attendance_percentage < 75:
                st.warning(f"⚠️ Your attendance is below 75%! You need to attend {int((0.75 * total_classes - present_days) / 0.25)} more classes to reach 75%.")
            
            # Attendance calendar view
            st.subheader("Attendance Calendar")
            my_attendance['date'] = pd.to_datetime(my_attendance['date'])
            my_attendance = my_attendance.sort_values('date', ascending=False)
            
            # Create a simple calendar view
            month_data = my_attendance.head(30)
            
            # Display attendance records
            st.subheader("Recent Attendance Records")
            display_data = month_data[['date', 'class', 'status']].copy()
            display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
            
            # Color code the status
            def highlight_status(row):
                if row['status'] == 'Present':
                    return ['background-color: #90EE90'] * len(row)
                else:
                    return ['background-color: #FFB6C1'] * len(row)
            
            styled_df = display_data.style.apply(highlight_status, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Attendance chart
            st.subheader("Attendance Trend")
            weekly_data = my_attendance.set_index('date').resample('W')['status'].apply(
                lambda x: (x == 'Present').sum() / len(x) * 100 if len(x) > 0 else 0
            ).reset_index()
            weekly_data.columns = ['Week', 'Attendance %']
            
            fig = px.bar(weekly_data, x='Week', y='Attendance %',
                        title="Weekly Attendance Percentage",
                        color='Attendance %',
                        color_continuous_scale=['red', 'yellow', 'green'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance records found")
    
    with tab2:
        st.header("Apply for Leave")
        
        with st.form("leave_application"):
            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input("From Date", min_value=datetime.now().date())
                to_date = st.date_input("To Date", min_value=datetime.now().date())
            with col2:
                apply_to = st.selectbox("Apply To", 
                                       ["FAC001 - Dr. Smith", "FAC002 - Prof. Johnson", "admin001 - Admin"])
                reason = st.text_area("Reason for Leave", height=100)
            
            if st.form_submit_button("📤 Submit Application", use_container_width=True):
                if from_date > to_date:
                    st.error("❌ 'From Date' cannot be after 'To Date'")
                elif not reason:
                    st.error("❌ Please provide a reason for leave")
                else:
                    # Add leave application
                    new_application = {
                        'application_id': f"LA{len(st.session_state.leave_applications) + 1:03d}",
                        'student_id': st.session_state.user_id,
                        'from_date': from_date.strftime('%Y-%m-%d'),
                        'to_date': to_date.strftime('%Y-%m-%d'),
                        'reason': reason,
                        'status': 'Pending',
                        'applied_to': apply_to.split(' - ')[0],
                        'applied_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    st.session_state.leave_applications = pd.concat([
                        st.session_state.leave_applications,
                        pd.DataFrame([new_application])
                    ], ignore_index=True)
                    
                    st.success("✅ Leave application submitted successfully!")
                    st.balloons()
    
    with tab3:
        st.header("My Leave Applications")
        
        my_leaves = st.session_state.leave_applications[
            st.session_state.leave_applications['student_id'] == st.session_state.user_id
        ]
        
        if not my_leaves.empty:
            # Separate by status
            pending = my_leaves[my_leaves['status'] == 'Pending']
            approved = my_leaves[my_leaves['status'] == 'Approved']
            rejected = my_leaves[my_leaves['status'] == 'Rejected']
            
            if not pending.empty:
                st.subheader("⏳ Pending Applications")
                for _, leave in pending.iterrows():
                    with st.container():
                        st.info(f"**Application ID:** {leave['application_id']}  \n"
                               f"**Duration:** {leave['from_date']} to {leave['to_date']}  \n"
                               f"**Applied To:** {leave['applied_to']}  \n"
                               f"**Reason:** {leave['reason']}")
            
            if not approved.empty:
                st.subheader("✅ Approved Applications")
                for _, leave in approved.iterrows():
                    with st.container():
                        st.success(f"**Application ID:** {leave['application_id']}  \n"
                                 f"**Duration:** {leave['from_date']} to {leave['to_date']}  \n"
                                 f"**Reason:** {leave['reason']}")
            
            if not rejected.empty:
                st.subheader("❌ Rejected Applications")
                for _, leave in rejected.iterrows():
                    with st.container():
                        st.error(f"**Application ID:** {leave['application_id']}  \n"
                               f"**Duration:** {leave['from_date']} to {leave['to_date']}  \n"
                               f"**Reason:** {leave['reason']}")
        else:
            st.info("No leave applications found")

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.captcha = None
    st.rerun()

# Main app logic
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        # Add logout button in sidebar
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user_name}")
            st.markdown(f"**Role:** {st.session_state.user_type.capitalize()}")
            st.markdown(f"**ID:** {st.session_state.user_id}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
