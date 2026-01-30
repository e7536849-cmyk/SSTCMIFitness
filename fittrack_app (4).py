import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

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
            df_chart = df.set_index('date')['bmi']
            st.subheader("BMI History")
            st.line_chart(df_chart)

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
                df_chart = df.set_index('date')['total_hours']
                st.subheader("Sleep Duration History (hours)")
                st.line_chart(df_chart)
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
            
            df_chart = pd.DataFrame({
                'Exercise': list(exercise_counts.keys()),
                'Count': list(exercise_counts.values())
            })
            df_chart = df_chart.set_index('Exercise')
            st.subheader("Exercise Frequency")
            st.bar_chart(df_chart)
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

# AI Insights and Recommendations
def ai_insights():
    st.header("🤖 AI Fitness Coach")
    
    user_data = get_user_data()
    
    # Create tabs for different AI features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💪 Workout Recommendations", 
        "🎯 Improvement Advice",
        "🍎 Meal Suggestions",
        "😴 Sleep Insights",
        "📈 Progress Predictions"
    ])
    
    with tab1:
        st.subheader("Personalized Workout Recommendations")
        
        if not user_data['napfa_history']:
            st.info("📝 Complete a NAPFA test first to get personalized workout recommendations!")
        else:
            latest_napfa = user_data['napfa_history'][-1]
            grades = latest_napfa['grades']
            
            st.write(f"**Based on your latest NAPFA test ({latest_napfa['date']}):**")
            st.write(f"**Total Score:** {latest_napfa['total']} | **Medal:** {latest_napfa['medal']}")
            
            # AI-generated workout plan
            workout_plan = []
            
            # Analyze each test component
            if grades['SU'] < 3:
                workout_plan.append({
                    'Focus': 'Core Strength (Sit-ups)',
                    'Exercises': 'Planks (3x30s), Bicycle crunches (3x15), Russian twists (3x20)',
                    'Frequency': '4-5 times per week',
                    'Tips': 'Focus on slow, controlled movements. Engage your core throughout.'
                })
            
            if grades['SBJ'] < 3:
                workout_plan.append({
                    'Focus': 'Explosive Power (Broad Jump)',
                    'Exercises': 'Box jumps (3x10), Squat jumps (3x12), Lunge jumps (3x10 each leg)',
                    'Frequency': '3-4 times per week',
                    'Tips': 'Land softly and focus on explosive power from your legs.'
                })
            
            if grades['SAR'] < 3:
                workout_plan.append({
                    'Focus': 'Flexibility (Sit and Reach)',
                    'Exercises': 'Hamstring stretches (hold 30s), Toe touches (3x10), Seated forward bend (hold 45s)',
                    'Frequency': 'Daily, especially after workouts',
                    'Tips': 'Stretch when muscles are warm. Never bounce - hold steady stretches.'
                })
            
            if grades['PU'] < 3:
                workout_plan.append({
                    'Focus': 'Upper Body Strength (Pull-ups)',
                    'Exercises': 'Assisted pull-ups (3x5), Negative pull-ups (3x3), Dead hangs (3x20s)',
                    'Frequency': '3-4 times per week',
                    'Tips': 'Build up slowly. Use resistance bands for assistance if needed.'
                })
            
            if grades['SR'] < 3:
                workout_plan.append({
                    'Focus': 'Agility & Speed (Shuttle Run)',
                    'Exercises': 'Ladder drills (5 mins), Cone drills (3x5), High knees (3x30s)',
                    'Frequency': '3 times per week',
                    'Tips': 'Focus on quick direction changes and maintaining low center of gravity.'
                })
            
            if grades['RUN'] < 3:
                workout_plan.append({
                    'Focus': 'Endurance (2.4km Run)',
                    'Exercises': 'Interval training (400m sprints with rest), Long slow runs (3-5km), Tempo runs',
                    'Frequency': '4-5 times per week',
                    'Tips': 'Build endurance gradually. Mix steady runs with interval training.'
                })
            
            if workout_plan:
                st.warning("🎯 **Areas needing improvement:**")
                for plan in workout_plan:
                    with st.expander(f"🏋️ {plan['Focus']}", expanded=True):
                        st.write(f"**Exercises:** {plan['Exercises']}")
                        st.write(f"**Frequency:** {plan['Frequency']}")
                        st.write(f"💡 **Tips:** {plan['Tips']}")
            else:
                st.success("🌟 Excellent! All your NAPFA components are strong. Focus on maintaining your performance with varied workouts.")
                st.info("**Maintenance Plan:** Mix cardio, strength training, and flexibility work 4-5 times per week to stay in top shape!")
    
    with tab2:
        st.subheader("AI Improvement Advice")
        
        if not user_data['napfa_history']:
            st.info("📝 Complete a NAPFA test first to get improvement advice!")
        else:
            latest_napfa = user_data['napfa_history'][-1]
            grades = latest_napfa['grades']
            
            # Find weakest areas
            weak_areas = [(test, grade) for test, grade in grades.items() if grade < 3]
            strong_areas = [(test, grade) for test, grade in grades.items() if grade >= 4]
            
            if weak_areas:
                st.error("⚠️ **Priority Areas for Improvement:**")
                
                test_names = {
                    'SU': 'Sit-Ups',
                    'SBJ': 'Standing Broad Jump',
                    'SAR': 'Sit and Reach',
                    'PU': 'Pull-Ups',
                    'SR': 'Shuttle Run',
                    'RUN': '2.4km Run'
                }
                
                for test, grade in sorted(weak_areas, key=lambda x: x[1]):
                    with st.expander(f"📍 {test_names[test]} (Grade {grade})"):
                        if test == 'SU':
                            st.write("**Why it matters:** Core strength is fundamental for all movements and injury prevention.")
                            st.write("**Quick win:** Do 3 sets of planks daily, increasing hold time weekly.")
                            st.write("**Long-term:** Add weighted core exercises once you reach Grade 3.")
                        elif test == 'SBJ':
                            st.write("**Why it matters:** Lower body power helps in sports and daily activities.")
                            st.write("**Quick win:** Practice jump squats 3x per week, focusing on explosive power.")
                            st.write("**Long-term:** Progressive plyometric training will significantly improve your distance.")
                        elif test == 'SAR':
                            st.write("**Why it matters:** Flexibility prevents injuries and improves overall mobility.")
                            st.write("**Quick win:** Stretch hamstrings and lower back daily for 10 minutes.")
                            st.write("**Long-term:** Consider yoga or dedicated flexibility sessions 2x per week.")
                        elif test == 'PU':
                            st.write("**Why it matters:** Upper body strength is crucial for overall fitness balance.")
                            st.write("**Quick win:** Start with assisted pull-ups or negatives every other day.")
                            st.write("**Long-term:** Gradually decrease assistance until you can do full pull-ups.")
                        elif test == 'SR':
                            st.write("**Why it matters:** Agility and speed are essential for sports performance.")
                            st.write("**Quick win:** Practice quick direction changes and footwork drills 3x weekly.")
                            st.write("**Long-term:** Join a sport that requires agility (basketball, badminton, football).")
                        elif test == 'RUN':
                            st.write("**Why it matters:** Cardiovascular endurance affects overall health and stamina.")
                            st.write("**Quick win:** Run 3-4 times weekly, starting at comfortable pace and distance.")
                            st.write("**Long-term:** Build up to 20-30km per week with mixed pace training.")
            
            if strong_areas:
                st.success("💪 **Your Strengths:**")
                for test, grade in strong_areas:
                    st.write(f"✓ {test_names[test]}: Grade {grade} - Keep it up!")
    
    with tab3:
        st.subheader("Meal Suggestions Based on Your Goals")
        
        if not user_data['bmi_history']:
            st.info("📝 Calculate your BMI first to get personalized meal suggestions!")
        else:
            latest_bmi = user_data['bmi_history'][-1]
            bmi_value = latest_bmi['bmi']
            category = latest_bmi['category']
            
            st.write(f"**Current BMI:** {bmi_value} ({category})")
            
            if category == "Underweight":
                st.warning("🍽️ **Goal: Healthy Weight Gain**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Oatmeal with banana, nuts, and honey")
                st.write("- Whole grain toast with peanut butter and scrambled eggs")
                st.write("- Smoothie with milk, banana, oats, and protein powder")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Chicken rice with extra chicken and vegetables")
                st.write("- Salmon with quinoa and roasted vegetables")
                st.write("- Lean beef with sweet potato and broccoli")
                
                st.write("\n**Snacks:**")
                st.write("- Trail mix (nuts, dried fruits)")
                st.write("- Greek yogurt with granola")
                st.write("- Whole grain crackers with cheese")
                
                st.info("💡 **Tips:** Eat 5-6 smaller meals, focus on nutrient-dense foods, stay hydrated!")
                
            elif category == "Normal":
                st.success("🎯 **Goal: Maintain Healthy Weight**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Greek yogurt with berries and granola")
                st.write("- Whole grain toast with avocado and eggs")
                st.write("- Smoothie bowl with fruits and nuts")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Grilled chicken with brown rice and vegetables")
                st.write("- Fish with quinoa and salad")
                st.write("- Tofu stir-fry with mixed vegetables")
                
                st.write("\n**Snacks:**")
                st.write("- Fresh fruits (apple, orange, banana)")
                st.write("- Vegetable sticks with hummus")
                st.write("- A handful of almonds")
                
                st.info("💡 **Tips:** Balanced portions, eat colorful vegetables, stay active!")
                
            elif category == "Overweight" or category == "Obesity":
                st.warning("🥗 **Goal: Healthy Weight Loss**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Egg white omelette with vegetables")
                st.write("- Oatmeal with berries (no added sugar)")
                st.write("- Green smoothie with spinach, cucumber, apple")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Grilled fish with steamed vegetables")
                st.write("- Chicken salad with olive oil dressing")
                st.write("- Vegetable soup with lean protein")
                
                st.write("\n**Snacks:**")
                st.write("- Carrot/cucumber sticks")
                st.write("- Apple slices")
                st.write("- Unsalted nuts (small portion)")
                
                st.info("💡 **Tips:** Portion control, avoid sugary drinks, drink water before meals, eat slowly!")
            
            st.write("\n---")
            st.write("**General Nutrition Tips for Athletes:**")
            st.write("🥤 Drink 8-10 glasses of water daily")
            st.write("🥦 Eat vegetables with every meal")
            st.write("🍗 Include lean protein in each meal")
            st.write("🍚 Choose whole grains over refined carbs")
            st.write("🚫 Limit processed foods and sugary snacks")
    
    with tab4:
        st.subheader("Sleep Quality Insights")
        
        if not user_data['sleep_history']:
            st.info("📝 Track your sleep first to get personalized insights!")
        else:
            # Analyze sleep data
            sleep_data = user_data['sleep_history']
            
            if len(sleep_data) >= 3:
                # Calculate average sleep
                total_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data])
                avg_hours = total_hours / len(sleep_data)
                
                st.metric("Average Sleep Duration", f"{avg_hours:.1f} hours")
                
                # Sleep quality analysis
                excellent_count = sum(1 for s in sleep_data if s['quality'] == 'Excellent')
                good_count = sum(1 for s in sleep_data if s['quality'] == 'Good')
                fair_count = sum(1 for s in sleep_data if s['quality'] == 'Fair')
                poor_count = sum(1 for s in sleep_data if s['quality'] == 'Poor')
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Excellent", excellent_count)
                col2.metric("Good", good_count)
                col3.metric("Fair", fair_count)
                col4.metric("Poor", poor_count)
                
                st.write("---")
                
                # Personalized advice
                if avg_hours >= 8:
                    st.success("🌟 **Excellent Sleep Habits!**")
                    st.write("You're getting enough sleep for optimal recovery and performance.")
                    st.write("\n**Tips to maintain:**")
                    st.write("- Keep a consistent sleep schedule, even on weekends")
                    st.write("- Your current routine is working - stick with it!")
                elif avg_hours >= 7:
                    st.info("👍 **Good Sleep Duration**")
                    st.write("You're close to the optimal 8-10 hours for teenagers.")
                    st.write("\n**To improve:**")
                    st.write("- Try going to bed 15-30 minutes earlier")
                    st.write("- Avoid screens 1 hour before bedtime")
                    st.write("- Keep your room cool and dark")
                elif avg_hours >= 6:
                    st.warning("⚠️ **Sleep More for Better Performance**")
                    st.write("You need more sleep for optimal growth and recovery.")
                    st.write("\n**Action plan:**")
                    st.write("- Set a bedtime alarm 30 minutes before sleep time")
                    st.write("- Reduce afternoon caffeine")
                    st.write("- Create a relaxing bedtime routine")
                else:
                    st.error("🚨 **Sleep Deficit Alert**")
                    st.write("Insufficient sleep affects your NAPFA performance and health!")
                    st.write("\n**Urgent actions:**")
                    st.write("- Prioritize sleep - aim for 8+ hours")
                    st.write("- Remove ALL screens from bedroom")
                    st.write("- Talk to parents/guardians about better sleep schedule")
                
                st.write("\n---")
                st.write("**Sleep Optimization Tips:**")
                st.write("😴 Go to bed and wake up at the same time daily")
                st.write("📱 No screens 1 hour before bed (blue light disrupts sleep)")
                st.write("🏃 Exercise earlier in the day (not right before bed)")
                st.write("☕ Avoid caffeine after 2 PM")
                st.write("🌡️ Keep room cool (18-20°C is ideal)")
                st.write("📚 Try reading a book before sleep")
                st.write("🧘 Practice relaxation techniques (deep breathing)")
            else:
                st.info("Track your sleep for at least 3 days to get detailed insights!")
    
    with tab5:
        st.subheader("Progress Predictions")
        
        # Check if user has goals
        if not user_data['goals']:
            st.info("📝 Set a goal first to get progress predictions!")
        else:
            st.write("**Your Goals Progress Forecast:**")
            
            for idx, goal in enumerate(user_data['goals']):
                with st.expander(f"🎯 {goal['type']} - {goal['target']}", expanded=True):
                    progress = goal['progress']
                    target_date = datetime.strptime(goal['date'], '%Y-%m-%d')
                    created_date = datetime.strptime(goal['created'], '%Y-%m-%d')
                    today = datetime.now()
                    
                    # Calculate days
                    days_total = (target_date - created_date).days
                    days_passed = (today - created_date).days
                    days_remaining = (target_date - today).days
                    
                    # Progress bar
                    st.progress(progress / 100)
                    st.write(f"**Current Progress:** {progress}%")
                    st.write(f"**Days Remaining:** {days_remaining} days")
                    
                    # AI Prediction
                    if days_passed > 0:
                        progress_per_day = progress / days_passed
                        predicted_progress = progress + (progress_per_day * days_remaining)
                        
                        if predicted_progress >= 100:
                            days_to_complete = int((100 - progress) / progress_per_day) if progress_per_day > 0 else 999
                            completion_date = today + timedelta(days=days_to_complete)
                            
                            if days_to_complete <= days_remaining:
                                st.success(f"🎉 **On Track!** At your current pace, you'll reach your goal by {completion_date.strftime('%B %d, %Y')} ({days_to_complete} days)")
                                st.write("Keep up the great work! 💪")
                            else:
                                st.info(f"📅 You'll reach your goal around {completion_date.strftime('%B %d, %Y')}")
                                st.write("You might need a bit more time, but you're making progress!")
                        else:
                            st.warning(f"⚠️ **Need to Speed Up!** At your current pace, you'll reach {predicted_progress:.0f}% by the target date.")
                            
                            # Calculate needed pace
                            needed_progress_per_day = (100 - progress) / days_remaining if days_remaining > 0 else 0
                            improvement_factor = needed_progress_per_day / progress_per_day if progress_per_day > 0 else 2
                            
                            st.write(f"**Recommendation:** Increase your effort by {improvement_factor:.1f}x to reach your goal on time!")
                            
                            # Specific advice based on goal type
                            if goal['type'] == "NAPFA Improvement":
                                st.write("💡 **Action:** Follow your AI workout plan more consistently")
                            elif goal['type'] == "Weight Loss" or goal['type'] == "Muscle Gain":
                                st.write("💡 **Action:** Review your meal plan and increase workout frequency")
                            elif goal['type'] == "Endurance":
                                st.write("💡 **Action:** Add one more cardio session per week")
                            elif goal['type'] == "Flexibility":
                                st.write("💡 **Action:** Stretch daily for 15 minutes")
                    else:
                        st.info("Keep tracking your progress to get predictions!")
        
        # NAPFA predictions
        if user_data['napfa_history'] and len(user_data['napfa_history']) >= 2:
            st.write("\n---")
            st.subheader("📊 NAPFA Score Trend")
            
            napfa_scores = [test['total'] for test in user_data['napfa_history']]
            napfa_dates = [test['date'] for test in user_data['napfa_history']]
            
            # Calculate trend
            score_diff = napfa_scores[-1] - napfa_scores[0]
            
            if score_diff > 0:
                st.success(f"📈 Your NAPFA total improved by {score_diff} points!")
                st.write(f"From {napfa_scores[0]} to {napfa_scores[-1]}")
                
                # Predict next score
                if len(napfa_scores) >= 2:
                    avg_improvement = score_diff / (len(napfa_scores) - 1)
                    predicted_next = napfa_scores[-1] + avg_improvement
                    
                    st.write(f"\n**Prediction:** If you maintain this pace, your next test could be around {predicted_next:.0f} points")
                    
                    # Medal prediction
                    if predicted_next >= 21:
                        st.write("🥇 Potential Gold medal!")
                    elif predicted_next >= 15:
                        st.write("🥈 Potential Silver medal!")
                    elif predicted_next >= 9:
                        st.write("🥉 Potential Bronze medal!")
                        
            elif score_diff < 0:
                st.warning(f"📉 Your score decreased by {abs(score_diff)} points")
                st.write("**Recommendation:** Review your training plan and increase consistency")
            else:
                st.info("Your score stayed the same. Time to push harder!")

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
                           ["🤖 AI Insights", "BMI Calculator", "NAPFA Test", "Sleep Tracker", 
                            "Exercise Log", "Set Goals", "Training Schedule"])
    
    # Display selected page
    if page == "🤖 AI Insights":
        ai_insights()
    elif page == "BMI Calculator":
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
