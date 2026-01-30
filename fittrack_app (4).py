import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# SST Color Palette
SST_COLORS = {
    'red': '#d32f2f',
    'blue': '#1976d2',
    'gray': '#5a5a5a',
    'light_gray': '#e0e0e0',
    'white': '#ffffff',
    'dark': '#2c2c2c'
}

# Configure page
st.set_page_config(
    page_title="FitTrack - SST Fitness Companion",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SST styling
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
    }}
    .main-header {{
        background: linear-gradient(135deg, {SST_COLORS['red']} 0%, #b71c1c 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(211, 47, 47, 0.3);
    }}
    .stat-card {{
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {SST_COLORS['blue']};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
    }}
    .grade-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 6px;
        font-weight: bold;
        color: white;
        margin: 5px;
    }}
    .grade-5 {{ background: #4caf50; }}
    .grade-4 {{ background: #8bc34a; }}
    .grade-3 {{ background: #ffc107; }}
    .grade-2 {{ background: #ff9800; }}
    .grade-1 {{ background: #f44336; }}
    h1, h2, h3 {{ color: {SST_COLORS['dark']}; }}
    .stButton>button {{
        background: linear-gradient(135deg, {SST_COLORS['blue']} 0%, #1565c0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 30px;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        transform: translateY(-2px);
    }}
    </style>
""", unsafe_allow_html=True)

# Data storage file
DATA_FILE = 'fittrack_users.json'

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users_data' not in st.session_state:
    st.session_state.users_data = {}

# Load user data
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user data
def save_users(users_data):
    with open(DATA_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

# Load data on startup
st.session_state.users_data = load_users()

# Get current user data
def get_user_data():
    if st.session_state.username in st.session_state.users_data:
        return st.session_state.users_data[st.session_state.username]
    return None

# Update user data
def update_user_data(data):
    st.session_state.users_data[st.session_state.username] = data
    save_users(st.session_state.users_data)

# NAPFA grading standards
NAPFA_STANDARDS = {
    12: {
        'm': {
            'SU': [[36,32,28,24,20], False],
            'SBJ': [[198,190,182,174,166], False],
            'SAR': [[39,37,34,30,25], False],
            'PU': [[6,5,4,3,2], False],
            'SR': [[10.8,11.2,11.6,12.1,12.6], True],
            'RUN': [[9.67,10.42,11.17,12.0,12.75], True]
        },
        'f': {
            'SU': [[29,25,21,17,13], False],
            'SBJ': [[167,159,150,141,132], False],
            'SAR': [[39,37,34,30,25], False],
            'PU': [[15,13,10,7,3], False],
            'SR': [[11.5,11.9,12.4,12.9,13.5], True],
            'RUN': [[11.0,11.75,12.67,13.42,14.42], True]
        }
    },
    13: {
        'm': {
            'SU': [[38,34,30,26,22], False],
            'SBJ': [[208,200,192,184,176], False],
            'SAR': [[40,38,35,31,26], False],
            'PU': [[8,7,6,5,4], False],
            'SR': [[10.5,10.9,11.3,11.8,12.3], True],
            'RUN': [[9.33,10.08,10.83,11.67,12.42], True]
        },
        'f': {
            'SU': [[31,27,23,19,15], False],
            'SBJ': [[172,164,155,146,137], False],
            'SAR': [[40,38,35,31,26], False],
            'PU': [[16,14,11,8,4], False],
            'SR': [[11.3,11.7,12.2,12.7,13.3], True],
            'RUN': [[10.75,11.5,12.42,13.17,14.17], True]
        }
    },
    14: {
        'm': {
            'SU': [[40,36,32,28,24], False],
            'SBJ': [[218,210,202,194,186], False],
            'SAR': [[41,39,36,32,27], False],
            'PU': [[10,9,8,7,6], False],
            'SR': [[10.2,10.6,11.0,11.5,12.0], True],
            'RUN': [[9.0,9.75,10.5,11.33,12.08], True]
        },
        'f': {
            'SU': [[33,29,25,21,17], False],
            'SBJ': [[176,168,159,150,141], False],
            'SAR': [[41,39,36,32,27], False],
            'PU': [[17,15,12,9,5], False],
            'SR': [[11.1,11.5,12.0,12.5,13.1], True],
            'RUN': [[10.5,11.25,12.17,12.92,13.92], True]
        }
    },
    15: {
        'm': {
            'SU': [[42,38,34,30,26], False],
            'SBJ': [[228,220,212,204,196], False],
            'SAR': [[42,40,37,33,28], False],
            'PU': [[12,11,10,9,8], False],
            'SR': [[9.9,10.3,10.7,11.2,11.7], True],
            'RUN': [[8.67,9.42,10.17,11.0,11.75], True]
        },
        'f': {
            'SU': [[35,31,27,23,19], False],
            'SBJ': [[180,172,163,154,145], False],
            'SAR': [[42,40,37,33,28], False],
            'PU': [[18,16,13,10,6], False],
            'SR': [[10.9,11.3,11.8,12.3,12.9], True],
            'RUN': [[10.25,11.0,11.92,12.67,13.67], True]
        }
    },
    16: {
        'm': {
            'SU': [[44,40,36,32,28], False],
            'SBJ': [[238,230,222,214,206], False],
            'SAR': [[43,41,38,34,29], False],
            'PU': [[14,13,12,11,10], False],
            'SR': [[9.6,10.0,10.4,10.9,11.4], True],
            'RUN': [[8.33,9.08,9.83,10.67,11.42], True]
        },
        'f': {
            'SU': [[37,33,29,25,21], False],
            'SBJ': [[184,176,167,158,149], False],
            'SAR': [[43,41,38,34,29], False],
            'PU': [[19,17,14,11,7], False],
            'SR': [[10.7,11.1,11.6,12.1,12.7], True],
            'RUN': [[10.0,10.75,11.67,12.42,13.42], True]
        }
    }
}

def calc_grade(score, cutoffs, reverse):
    """Calculate grade from score and cutoffs"""
    for i, cutoff in enumerate(cutoffs):
        if reverse:
            if score <= cutoff:
                return 5 - i
        else:
            if score >= cutoff:
                return 5 - i
    return 0

# Login/Registration Page
def login_page():
    st.markdown('<div class="main-header"><h1>🏋️ FitTrack</h1><p>School of Science and Technology Singapore</p><p>Your Personal Fitness Companion</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Welcome Back!")
        username = st.text_input("Username", key="login_username")
        if st.button("Login", key="login_btn"):
            if username in st.session_state.users_data:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("User not found. Please create an account.")
    
    with tab2:
        st.subheader("Create Account")
        new_username = st.text_input("Choose Username", key="reg_username")
        full_name = st.text_input("Full Name", key="reg_name")
        age = st.number_input("Age", min_value=12, max_value=18, value=14, key="reg_age")
        gender = st.selectbox("Gender", ["Male", "Female"], key="reg_gender")
        
        if st.button("Create Account", key="register_btn"):
            if not new_username or not full_name:
                st.error("Please fill in all fields")
            elif new_username in st.session_state.users_data:
                st.error("Username already exists")
            else:
                st.session_state.users_data[new_username] = {
                    'name': full_name,
                    'age': age,
                    'gender': 'm' if gender == "Male" else 'f',
                    'created': datetime.now().isoformat(),
                    'bmi_history': [],
                    'napfa_history': [],
                    'sleep_history': [],
                    'exercises': [],
                    'goals': [],
                    'schedule': []
                }
                save_users(st.session_state.users_data)
                st.success("Account created! Please login.")

# BMI Calculator
def bmi_calculator():
    st.header("📊 BMI Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=60.0, step=0.1)
    with col2:
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.65, step=0.01)
    
    if st.button("Calculate BMI"):
        bmi = weight / (height * height)
        
        if bmi < 18.5:
            category = "Underweight"
            color = "#2196f3"
        elif bmi < 25:
            category = "Normal"
            color = "#4caf50"
        elif bmi < 30:
            category = "Overweight"
            color = "#ff9800"
        else:
            category = "Obesity"
            color = "#f44336"
        
        # Save to history
        user_data = get_user_data()
        user_data['bmi_history'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'bmi': round(bmi, 2),
            'weight': weight,
            'height': height,
            'category': category
        })
        update_user_data(user_data)
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stat-card"><h2 style="color: {color};">BMI: {bmi:.2f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["gray"]};">Category: {category}</h2></div>', unsafe_allow_html=True)
        
        st.info(f"📈 You have {len(user_data['bmi_history'])} BMI record(s) saved.")
        
        # Show history chart if there's data
        if len(user_data['bmi_history']) > 1:
            df = pd.DataFrame(user_data['bmi_history'])
            fig = px.line(df, x='date', y='bmi', title='BMI History', 
                         markers=True, color_discrete_sequence=[SST_COLORS['blue']])
            st.plotly_chart(fig, use_container_width=True)

# NAPFA Test Calculator
def napfa_calculator():
    st.header("🏃 NAPFA Test Calculator")
    
    user_data = get_user_data()
    
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"], 
                            index=0 if user_data['gender'] == 'm' else 1)
    with col2:
        age = st.number_input("Age", min_value=12, max_value=16, value=user_data['age'])
    
    if age not in NAPFA_STANDARDS:
        st.error("Age must be between 12-16")
        return
    
    gender_key = 'm' if gender == "Male" else 'f'
    
    st.subheader("Enter Your Scores")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        situps = st.number_input("Sit-ups (1 min)", min_value=0, max_value=100, value=30)
        broadjump = st.number_input("Standing Broad Jump (cm)", min_value=0, max_value=300, value=200)
    with col2:
        sitreach = st.number_input("Sit and Reach (cm)", min_value=0, max_value=100, value=35)
        pullups = st.number_input("Pull-ups (30 sec)", min_value=0, max_value=50, value=8)
    with col3:
        shuttlerun = st.number_input("Shuttle Run (seconds)", min_value=5.0, max_value=20.0, value=10.5, step=0.1)
        run_time = st.text_input("2.4km Run (min:sec)", value="10:30")
    
    if st.button("Calculate Grades"):
        try:
            # Convert run time
            time_parts = run_time.split(':')
            run_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
            
            standards = NAPFA_STANDARDS[age][gender_key]
            
            scores = {
                'SU': situps,
                'SBJ': broadjump,
                'SAR': sitreach,
                'PU': pullups,
                'SR': shuttlerun,
                'RUN': run_minutes
            }
            
            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }
            
            grades = {}
            total = 0
            min_grade = 5
            
            for test in scores:
                grade = calc_grade(scores[test], standards[test][0], standards[test][1])
                grades[test] = grade
                total += grade
                min_grade = min(min_grade, grade)
            
            # Determine medal
            if total >= 21 and min_grade >= 3:
                medal = "🥇 Gold"
                medal_color = "#FFD700"
            elif total >= 15 and min_grade >= 2:
                medal = "🥈 Silver"
                medal_color = "#C0C0C0"
            elif total >= 9 and min_grade >= 1:
                medal = "🥉 Bronze"
                medal_color = "#CD7F32"
            else:
                medal = "No Medal"
                medal_color = SST_COLORS['gray']
            
            # Save to history
            user_data['napfa_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'age': age,
                'gender': gender_key,
                'scores': scores,
                'grades': grades,
                'total': total,
                'medal': medal
            })
            update_user_data(user_data)
            
            # Display results
            st.markdown("### Results")
            
            results_data = []
            for test, grade in grades.items():
                results_data.append({
                    'Test': test_names[test],
                    'Score': scores[test],
                    'Grade': grade
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["blue"]};">Total: {total}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {medal_color};">Medal: {medal}</h2></div>', unsafe_allow_html=True)
            
            st.info(f"📈 You have {len(user_data['napfa_history'])} NAPFA test(s) saved.")
            
        except Exception as e:
            st.error(f"Error calculating grades: {str(e)}")

# Sleep Tracker
def sleep_tracker():
    st.header("😴 Sleep Tracker")
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_start = st.time_input("Sleep Start Time", value=None)
    with col2:
        sleep_end = st.time_input("Wake Up Time", value=None)
    
    if st.button("Calculate Sleep"):
        if sleep_start and sleep_end:
            # Convert to datetime for calculation
            start = datetime.combine(datetime.today(), sleep_start)
            end = datetime.combine(datetime.today(), sleep_end)
            
            # Handle overnight sleep
            if end < start:
                end += timedelta(days=1)
            
            diff = end - start
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if hours >= 8:
                quality = "Excellent"
                color = "#4caf50"
                advice = "✓ Great job! You're getting enough sleep."
            elif hours >= 7:
                quality = "Good"
                color = "#8bc34a"
                advice = "👍 Good sleep duration. Try to get a bit more."
            elif hours >= 6:
                quality = "Fair"
                color = "#ff9800"
                advice = "⚠️ You need more sleep. Aim for 8-10 hours per night."
            else:
                quality = "Poor"
                color = "#f44336"
                advice = "⚠️ You need more sleep. Aim for 8-10 hours per night."
            
            # Save to history
            user_data = get_user_data()
            user_data['sleep_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sleep_start': str(sleep_start),
                'sleep_end': str(sleep_end),
                'hours': hours,
                'minutes': minutes,
                'quality': quality
            })
            update_user_data(user_data)
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {color};">Sleep Duration: {hours}h {minutes}m</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["blue"]};">Quality: {quality}</h2></div>', unsafe_allow_html=True)
            
            st.info(advice)
            st.info(f"📈 You have {len(user_data['sleep_history'])} sleep record(s) saved.")
            
            # Show history chart if there's data
            if len(user_data['sleep_history']) > 1:
                df = pd.DataFrame(user_data['sleep_history'])
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                fig = px.line(df, x='date', y='total_hours', title='Sleep Duration History', 
                             markers=True, color_discrete_sequence=[SST_COLORS['blue']])
                fig.update_yaxes(title_text="Hours")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Please enter both sleep start and end times")

# Exercise Logger
def exercise_logger():
    st.header("💪 Exercise Logger")
    
    with st.form("exercise_form"):
        exercise_name = st.text_input("Exercise Name", placeholder="e.g., Running, Swimming")
        
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        with col2:
            intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])
        
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("Log Exercise")
        
        if submitted:
            if exercise_name:
                user_data = get_user_data()
                user_data['exercises'].insert(0, {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'name': exercise_name,
                    'duration': duration,
                    'intensity': intensity,
                    'notes': notes
                })
                update_user_data(user_data)
                st.success("Exercise logged successfully!")
                st.rerun()
            else:
                st.error("Please enter exercise name")
    
    # Display exercise history
    user_data = get_user_data()
    if user_data['exercises']:
        st.subheader("Recent Exercises")
        df = pd.DataFrame(user_data['exercises'])
        st.dataframe(df[['date', 'name', 'duration', 'intensity']], use_container_width=True, hide_index=True)
        
        # Show summary chart
        if len(user_data['exercises']) > 0:
            exercise_counts = {}
            for ex in user_data['exercises']:
                exercise_counts[ex['name']] = exercise_counts.get(ex['name'], 0) + 1
            
            fig = px.bar(x=list(exercise_counts.keys()), y=list(exercise_counts.values()),
                        title="Exercise Frequency", labels={'x': 'Exercise', 'y': 'Count'},
                        color_discrete_sequence=[SST_COLORS['blue']])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No exercises logged yet.")

# Goal Setting
def goal_setting():
    st.header("🎯 Fitness Goals")
    
    with st.form("goal_form"):
        goal_type = st.selectbox("Goal Type", 
                                ["Weight Loss", "Muscle Gain", "NAPFA Improvement", 
                                 "Endurance", "Flexibility"])
        target = st.text_input("Target Value", placeholder="e.g., 60kg, Grade 5, 30 min run")
        target_date = st.date_input("Target Date")
        progress = st.slider("Current Progress (%)", 0, 100, 0)
        
        submitted = st.form_submit_button("Set Goal")
        
        if submitted:
            if target:
                user_data = get_user_data()
                user_data['goals'].append({
                    'type': goal_type,
                    'target': target,
                    'date': target_date.strftime('%Y-%m-%d'),
                    'progress': progress,
                    'created': datetime.now().strftime('%Y-%m-%d')
                })
                update_user_data(user_data)
                st.success("Goal set successfully!")
                st.rerun()
            else:
                st.error("Please enter target value")
    
    # Display goals
    user_data = get_user_data()
    if user_data['goals']:
        st.subheader("Your Goals")
        for idx, goal in enumerate(user_data['goals']):
            with st.expander(f"{goal['type']} - {goal['target']}"):
                st.write(f"**Target Date:** {goal['date']}")
                st.write(f"**Created:** {goal['created']}")
                st.progress(goal['progress'] / 100)
                st.write(f"Progress: {goal['progress']}%")
    else:
        st.info("No goals set yet.")

# Schedule Manager
def schedule_manager():
    st.header("📅 Training Schedule")
    
    with st.form("schedule_form"):
        day = st.selectbox("Day of Week", 
                          ["Monday", "Tuesday", "Wednesday", "Thursday", 
                           "Friday", "Saturday", "Sunday"])
        activity = st.text_input("Activity", placeholder="e.g., Morning run")
        
        col1, col2 = st.columns(2)
        with col1:
            time = st.time_input("Time")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        
        submitted = st.form_submit_button("Add to Schedule")
        
        if submitted:
            if activity:
                user_data = get_user_data()
                user_data['schedule'].append({
                    'day': day,
                    'activity': activity,
                    'time': str(time),
                    'duration': duration
                })
                update_user_data(user_data)
                st.success("Activity added to schedule!")
                st.rerun()
            else:
                st.error("Please enter activity name")
    
    # Display schedule
    user_data = get_user_data()
    if user_data['schedule']:
        st.subheader("Weekly Schedule")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            day_activities = [s for s in user_data['schedule'] if s['day'] == day]
            if day_activities:
                st.markdown(f"### {day}")
                for activity in day_activities:
                    st.markdown(f'<div class="stat-card"><strong>{activity["activity"]}</strong><br>{activity["time"]} - {activity["duration"]} minutes</div>', 
                              unsafe_allow_html=True)
    else:
        st.info("No activities scheduled yet.")

# Main App
def main_app():
    user_data = get_user_data()
    
    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="main-header"><h1>🏋️ FitTrack</h1><p>Welcome back, {user_data["name"]}!</p></div>', 
                   unsafe_allow_html=True)
    with col2:
        st.write("")
        st.write("")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a feature:", 
                           ["BMI Calculator", "NAPFA Test", "Sleep Tracker", 
                            "Exercise Log", "Set Goals", "Training Schedule"])
    
    # Display selected page
    if page == "BMI Calculator":
        bmi_calculator()
    elif page == "NAPFA Test":
        napfa_calculator()
    elif page == "Sleep Tracker":
        sleep_tracker()
    elif page == "Exercise Log":
        exercise_logger()
    elif page == "Set Goals":
        goal_setting()
    elif page == "Training Schedule":
        schedule_manager()

# Main execution
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
