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

# Body Type Calculator
def calculate_body_type(weight, height):
    """Calculate body type based on BMI and frame"""
    bmi = weight / (height * height)
    
    # Simplified body type classification
    if bmi < 18.5:
        return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
    elif bmi < 25:
        if bmi < 21.5:
            return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
        else:
            return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    elif bmi < 30:
        return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    else:
        return "Endomorph", "Larger bone structure, gains weight easily, slower metabolism"

# Recipe API Integration (using TheMealDB - free API)
def search_recipes_by_diet(diet_type, meal_type=""):
    """Search for recipes based on diet goals"""
    # This is a placeholder - TheMealDB API doesn't require auth
    # We'll create a curated list based on diet needs
    
    recipes = {
        "Weight Loss": [
            {"name": "Grilled Chicken Salad", "calories": 350, "protein": "35g", "carbs": "20g", "prep_time": "20 min",
             "ingredients": ["Chicken breast", "Mixed greens", "Cherry tomatoes", "Cucumber", "Olive oil", "Lemon"],
             "instructions": "1. Grill chicken breast until cooked\n2. Chop vegetables\n3. Mix greens with veggies\n4. Slice chicken on top\n5. Drizzle with olive oil and lemon"},
            
            {"name": "Steamed Fish with Vegetables", "calories": 320, "protein": "40g", "carbs": "15g", "prep_time": "25 min",
             "ingredients": ["White fish fillet", "Broccoli", "Carrots", "Ginger", "Soy sauce", "Garlic"],
             "instructions": "1. Season fish with ginger and garlic\n2. Steam fish for 15 min\n3. Steam vegetables separately\n4. Serve with light soy sauce"},
            
            {"name": "Egg White Omelette", "calories": 180, "protein": "20g", "carbs": "8g", "prep_time": "10 min",
             "ingredients": ["Egg whites (4)", "Spinach", "Mushrooms", "Tomatoes", "Black pepper"],
             "instructions": "1. Whisk egg whites\n2. Sauté vegetables\n3. Pour egg whites over veggies\n4. Cook until set"},
            
            {"name": "Greek Yogurt Bowl", "calories": 250, "protein": "18g", "carbs": "30g", "prep_time": "5 min",
             "ingredients": ["Greek yogurt", "Berries", "Chia seeds", "Honey (small amount)", "Almonds"],
             "instructions": "1. Add yogurt to bowl\n2. Top with berries\n3. Sprinkle chia seeds and chopped almonds\n4. Drizzle tiny bit of honey"},
            
            {"name": "Vegetable Soup", "calories": 150, "protein": "8g", "carbs": "25g", "prep_time": "30 min",
             "ingredients": ["Mixed vegetables", "Vegetable broth", "Garlic", "Onion", "Herbs"],
             "instructions": "1. Sauté garlic and onion\n2. Add chopped vegetables\n3. Pour in broth\n4. Simmer 20 minutes\n5. Season with herbs"}
        ],
        
        "Muscle Gain": [
            {"name": "Chicken Rice Bowl", "calories": 650, "protein": "50g", "carbs": "70g", "prep_time": "30 min",
             "ingredients": ["Chicken breast", "Brown rice", "Sweet potato", "Broccoli", "Olive oil"],
             "instructions": "1. Cook brown rice\n2. Grill or bake chicken\n3. Roast sweet potato\n4. Steam broccoli\n5. Combine in bowl with olive oil"},
            
            {"name": "Salmon with Quinoa", "calories": 700, "protein": "45g", "carbs": "60g", "prep_time": "25 min",
             "ingredients": ["Salmon fillet", "Quinoa", "Avocado", "Spinach", "Lemon"],
             "instructions": "1. Cook quinoa\n2. Bake salmon with lemon\n3. Sauté spinach\n4. Serve together with sliced avocado"},
            
            {"name": "Protein Smoothie Bowl", "calories": 550, "protein": "40g", "carbs": "65g", "prep_time": "10 min",
             "ingredients": ["Protein powder", "Banana", "Oats", "Peanut butter", "Milk", "Berries"],
             "instructions": "1. Blend protein powder, banana, oats, milk\n2. Pour into bowl\n3. Top with berries and peanut butter"},
            
            {"name": "Beef Stir Fry", "calories": 600, "protein": "48g", "carbs": "50g", "prep_time": "20 min",
             "ingredients": ["Lean beef", "Mixed vegetables", "Brown rice", "Soy sauce", "Garlic", "Ginger"],
             "instructions": "1. Cook brown rice\n2. Stir fry beef with garlic and ginger\n3. Add vegetables\n4. Season with soy sauce\n5. Serve over rice"},
            
            {"name": "Tuna Pasta", "calories": 620, "protein": "42g", "carbs": "75g", "prep_time": "20 min",
             "ingredients": ["Whole wheat pasta", "Canned tuna", "Cherry tomatoes", "Olive oil", "Garlic", "Basil"],
             "instructions": "1. Cook pasta\n2. Sauté garlic and tomatoes\n3. Add drained tuna\n4. Mix with pasta\n5. Top with fresh basil"}
        ],
        
        "Maintenance": [
            {"name": "Balanced Buddha Bowl", "calories": 500, "protein": "28g", "carbs": "55g", "prep_time": "25 min",
             "ingredients": ["Chickpeas", "Quinoa", "Mixed greens", "Avocado", "Cherry tomatoes", "Tahini"],
             "instructions": "1. Cook quinoa\n2. Roast chickpeas\n3. Arrange greens in bowl\n4. Add quinoa, chickpeas, tomatoes\n5. Top with avocado and tahini"},
            
            {"name": "Chicken Wrap", "calories": 480, "protein": "35g", "carbs": "45g", "prep_time": "15 min",
             "ingredients": ["Whole wheat wrap", "Grilled chicken", "Lettuce", "Tomato", "Hummus", "Cucumber"],
             "instructions": "1. Spread hummus on wrap\n2. Add lettuce and vegetables\n3. Place sliced chicken\n4. Roll tightly and cut"},
            
            {"name": "Egg Fried Rice", "calories": 520, "protein": "22g", "carbs": "62g", "prep_time": "20 min",
             "ingredients": ["Brown rice", "Eggs", "Mixed vegetables", "Soy sauce", "Spring onions"],
             "instructions": "1. Cook rice (preferably day-old)\n2. Scramble eggs separately\n3. Stir fry vegetables\n4. Add rice and eggs\n5. Season with soy sauce"},
            
            {"name": "Grilled Fish Tacos", "calories": 450, "protein": "32g", "carbs": "48g", "prep_time": "20 min",
             "ingredients": ["White fish", "Corn tortillas", "Cabbage", "Lime", "Greek yogurt", "Cilantro"],
             "instructions": "1. Season and grill fish\n2. Warm tortillas\n3. Shred cabbage\n4. Assemble tacos with fish and slaw\n5. Top with yogurt and cilantro"},
            
            {"name": "Oatmeal with Fruits", "calories": 380, "protein": "15g", "carbs": "58g", "prep_time": "10 min",
             "ingredients": ["Oats", "Milk", "Banana", "Berries", "Honey", "Nuts"],
             "instructions": "1. Cook oats with milk\n2. Slice banana\n3. Top with fruits and nuts\n4. Drizzle with honey"}
        ]
    }
    
    return recipes

# AI Helper Functions
def generate_ai_response(question, user_data):
    """Generate AI response based on user question and their data"""
    question_lower = question.lower()
    
    # Analyze user data for context
    has_napfa = len(user_data.get('napfa_history', [])) > 0
    has_bmi = len(user_data.get('bmi_history', [])) > 0
    has_sleep = len(user_data.get('sleep_history', [])) > 0
    
    # NAPFA related questions
    if 'napfa' in question_lower or 'pull' in question_lower or 'sit up' in question_lower or 'run' in question_lower:
        if has_napfa:
            latest = user_data['napfa_history'][-1]
            weak_tests = [test for test, grade in latest['grades'].items() if grade < 3]
            if weak_tests:
                return f"Based on your latest NAPFA test, I see you need work on: {', '.join(weak_tests)}. Check the 'Workout Recommendations' tab for specific exercises! Focus on consistency - train each weak area 3-4x per week."
            else:
                return f"Great NAPFA scores! Your total is {latest['total']} points. To maintain or improve: (1) Keep training all components weekly, (2) Focus on explosive power for jumps, (3) Mix steady runs with sprints, (4) Don't neglect flexibility!"
        else:
            return "Complete a NAPFA test first so I can give you personalized advice! Once you do, I'll analyze your weak areas and create a specific plan."
    
    # BMI/Weight related
    elif 'weight' in question_lower or 'bmi' in question_lower or 'lose' in question_lower or 'gain' in question_lower:
        if has_bmi:
            latest_bmi = user_data['bmi_history'][-1]
            category = latest_bmi['category']
            if category == "Normal":
                return f"Your BMI is {latest_bmi['bmi']} (Normal range). To maintain: eat balanced meals, exercise 4-5x/week, stay hydrated. Focus on building strength and endurance rather than weight change!"
            elif category == "Underweight":
                return "To gain healthy weight: (1) Eat 5-6 small meals daily, (2) Focus on protein + complex carbs, (3) Strength train 3-4x/week, (4) Drink smoothies with banana, oats, peanut butter. Check 'Meal Suggestions' for specific foods!"
            else:
                return "For healthy weight loss: (1) Create small calorie deficit (200-300 cal), (2) Eat lean protein + veggies each meal, (3) Do cardio 4-5x/week, (4) Avoid sugary drinks. Check 'Meal Suggestions' for detailed plan!"
        else:
            return "Calculate your BMI first! Then I can give you personalized nutrition and training advice for your goals."
    
    # Sleep related
    elif 'sleep' in question_lower or 'tired' in question_lower or 'energy' in question_lower:
        if has_sleep:
            sleep_data = user_data['sleep_history']
            avg_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / len(sleep_data)
            if avg_hours >= 8:
                return f"Your sleep is excellent at {avg_hours:.1f} hours! Keep it consistent. If still tired: check iron levels, reduce screen time before bed, and ensure quality sleep (dark, cool room)."
            else:
                return f"You're averaging {avg_hours:.1f} hours - you need 8-10 hours as a teen! Tips: (1) Set bedtime alarm, (2) No screens 1hr before bed, (3) Same sleep schedule daily, (4) Avoid caffeine after 2pm. Check 'Sleep Insights' for more!"
        else:
            return "Track your sleep for a few days first! Then I can analyze your patterns and give specific advice. Teenagers need 8-10 hours for optimal performance and recovery."
    
    # Strength training
    elif 'strength' in question_lower or 'muscle' in question_lower or 'strong' in question_lower:
        return "To build strength: (1) Focus on compound exercises (push-ups, pull-ups, squats), (2) Progressive overload - increase difficulty weekly, (3) Eat protein after workouts, (4) Rest 48hrs between training same muscles, (5) Start with bodyweight, add resistance gradually. Check 'Custom Workout Plan' for a complete program!"
    
    # Cardio/Endurance
    elif 'cardio' in question_lower or 'endurance' in question_lower or 'stamina' in question_lower:
        return "Build endurance with: (1) Start at comfortable pace - able to talk while running, (2) Gradually increase distance by 10% weekly, (3) Mix steady runs (30-45min) with intervals (sprint 1min, jog 2min x 8), (4) Cross-train with swimming/cycling, (5) Stay hydrated! Aim for 3-4 cardio sessions weekly."
    
    # Diet/Nutrition
    elif 'eat' in question_lower or 'food' in question_lower or 'diet' in question_lower or 'meal' in question_lower:
        return "For athletic performance: (1) Eat breakfast within 1hr of waking, (2) Balance each meal: lean protein + complex carbs + vegetables, (3) Pre-workout: banana + peanut butter, (4) Post-workout: protein + carbs within 1hr, (5) Stay hydrated - 8-10 glasses daily, (6) Limit processed foods and sugar. Check 'Meal Suggestions' for specific plans!"
    
    # Recovery
    elif 'recover' in question_lower or 'sore' in question_lower or 'rest' in question_lower:
        return "Recovery is crucial! (1) Sleep 8-10 hours, (2) Eat protein within 1hr post-workout, (3) Stay hydrated, (4) Active recovery: light walk/swim on rest days, (5) Stretch daily, (6) Ice sore muscles, (7) Rest 1-2 full days/week. Muscle soreness 24-48hrs after workout is normal (DOMS)!"
    
    # Motivation
    elif 'motivat' in question_lower or 'give up' in question_lower or 'hard' in question_lower:
        return "Stay motivated! 💪 (1) Set small, achievable goals, (2) Track progress - celebrate small wins, (3) Find a workout buddy, (4) Mix up your routine to stay interested, (5) Remember your 'why', (6) Progress isn't linear - some weeks are tough, (7) Focus on how you FEEL not just numbers. You've got this!"
    
    # Flexibility
    elif 'stretch' in question_lower or 'flexibility' in question_lower or 'flexib' in question_lower:
        return "Improve flexibility: (1) Stretch AFTER workouts when muscles are warm, (2) Hold each stretch 30-60 seconds, (3) Never bounce, (4) Stretch daily - even on rest days, (5) Focus on hamstrings, hip flexors, shoulders, (6) Try yoga 1-2x/week, (7) Breathe deeply while stretching. Flexibility improves injury prevention and performance!"
    
    # Injury
    elif 'injur' in question_lower or 'pain' in question_lower or 'hurt' in question_lower:
        return "⚠️ If you have pain (not soreness): (1) STOP that activity immediately, (2) Rest and ice the area, (3) See a doctor/physiotherapist if pain persists, (4) Don't train through pain - it makes injuries worse. Prevention: warm up properly, increase intensity gradually, use proper form, rest adequately. Your health comes first!"
    
    # Default helpful response
    else:
        return "I can help with: NAPFA training, strength building, cardio/endurance, nutrition/meals, weight management, sleep optimization, recovery, flexibility, injury prevention, and motivation! Try asking about any of these topics, or check the other tabs for detailed insights based on your data. What specific aspect of fitness would you like to know about?"

def generate_workout_exercises(focus, location, duration_min, fitness_level):
    """Generate exercises based on workout parameters"""
    exercises = []
    
    # Adjust sets/reps based on fitness level
    if fitness_level == "Beginner":
        sets, reps = 2, 10
        rest = "60-90 seconds"
    elif fitness_level == "Intermediate":
        sets, reps = 3, 12
        rest = "45-60 seconds"
    else:  # Advanced
        sets, reps = 4, 15
        rest = "30-45 seconds"
    
    # Generate exercises based on focus
    if focus in ["Upper Body Strength", "Strength Training"]:
        if location == "Home (no equipment)":
            exercises = [
                f"Push-ups: {sets} sets x {reps} reps (rest {rest})",
                f"Diamond push-ups: {sets} sets x {reps-5} reps",
                f"Pike push-ups: {sets} sets x {reps-3} reps",
                f"Tricep dips (chair): {sets} sets x {reps} reps",
                f"Plank shoulder taps: {sets} sets x {reps*2} taps"
            ]
        elif location == "Gym" or location == "School":
            exercises = [
                f"Pull-ups/Chin-ups: {sets} sets x max reps",
                f"Push-ups: {sets} sets x {reps+5} reps",
                f"Dumbbell shoulder press: {sets} sets x {reps} reps",
                f"Bent-over rows: {sets} sets x {reps} reps",
                f"Dips: {sets} sets x {reps} reps"
            ]
        else:
            exercises = [
                f"Pull-ups (bar/tree): {sets} sets x max reps",
                f"Push-ups: {sets} sets x {reps} reps",
                f"Bench dips: {sets} sets x {reps} reps",
                f"Inverted rows: {sets} sets x {reps} reps"
            ]
    
    elif focus in ["Lower Body & Core", "Lower Body"]:
        exercises = [
            f"Squats: {sets} sets x {reps+5} reps",
            f"Lunges: {sets} sets x {reps} reps each leg",
            f"Glute bridges: {sets} sets x {reps+5} reps",
            f"Calf raises: {sets} sets x {reps+10} reps",
            f"Plank: {sets} sets x 30-60 seconds",
            f"Russian twists: {sets} sets x {reps*2} total reps",
            f"Bicycle crunches: {sets} sets x {reps+5} reps"
        ]
    
    elif focus in ["Cardio & Endurance", "Cardio Training"]:
        if duration_min >= 60:
            exercises = [
                "Running: 30 minutes steady pace",
                "Interval sprints: 8 rounds (1 min sprint, 2 min jog)",
                "Jump rope: 3 sets x 3 minutes",
                "High knees: 3 sets x 1 minute",
                "Burpees: 3 sets x 12 reps"
            ]
        else:
            exercises = [
                "Running: 15-20 minutes steady pace",
                "Interval sprints: 6 rounds (1 min sprint, 90 sec jog)",
                "Jumping jacks: 3 sets x 50 reps",
                "Mountain climbers: 3 sets x 30 seconds"
            ]
    
    else:  # Full Body
        exercises = [
            f"Squats: {sets} sets x {reps} reps",
            f"Push-ups: {sets} sets x {reps} reps",
            f"Lunges: {sets} sets x {reps} reps each leg",
            f"Plank: {sets} sets x 45 seconds",
            f"Burpees: {sets} sets x {reps-2} reps",
            f"Sit-ups: {sets} sets x {reps+5} reps",
            f"Jump squats: {sets} sets x {reps} reps"
        ]
    
    return exercises

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
                    'schedule': [],
                    'saved_workout_plan': None
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🗓️ AI Schedule Generator",
        "🍳 Health Recipes",
        "💬 AI Chat Assistant",
        "📋 Custom Workout Plan",
        "💪 Workout Recommendations", 
        "🎯 Improvement Advice",
        "🍎 Meal Suggestions",
        "😴 Sleep Insights",
        "📈 Progress Predictions"
    ])
    
    with tab1:
        st.subheader("🗓️ Comprehensive AI Schedule Generator")
        st.write("Generate a complete personalized schedule based on your fitness data!")
        
        # Check if user has necessary data
        has_napfa = len(user_data.get('napfa_history', [])) > 0
        has_bmi = len(user_data.get('bmi_history', [])) > 0
        has_sleep = len(user_data.get('sleep_history', [])) > 0
        
        if not has_napfa or not has_bmi or not has_sleep:
            st.warning("⚠️ To generate a complete schedule, please complete:")
            if not has_napfa:
                st.write("- ❌ NAPFA Test")
            if not has_bmi:
                st.write("- ❌ BMI Calculation")
            if not has_sleep:
                st.write("- ❌ Sleep Tracking (at least 3 days)")
            st.info("Once you have this data, come back to generate your personalized schedule!")
        else:
            st.success("✅ All data available! Ready to generate your schedule.")
            
            # Get latest data
            latest_napfa = user_data['napfa_history'][-1]
            latest_bmi_record = user_data['bmi_history'][-1]
            latest_bmi = latest_bmi_record['bmi']
            
            # Calculate body type
            body_type, body_description = calculate_body_type(
                latest_bmi_record['weight'], 
                latest_bmi_record['height']
            )
            
            # BMI for the week
            week_ago = datetime.now() - timedelta(days=7)
            bmi_week = [b for b in user_data['bmi_history'] 
                       if datetime.strptime(b['date'], '%Y-%m-%d') >= week_ago]
            
            # Sleep for the week
            sleep_week = [s for s in user_data['sleep_history'] 
                         if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
            
            # Display current data
            st.write("### 📊 Your Current Data")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest BMI", f"{latest_bmi:.1f}")
                st.write(f"**Body Type:** {body_type}")
            with col2:
                st.metric("NAPFA Score", f"{latest_napfa['total']}/30")
                st.write(f"**Medal:** {latest_napfa['medal']}")
            with col3:
                if sleep_week:
                    avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_week]) / len(sleep_week)
                    st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
                    st.write(f"**Records:** {len(sleep_week)} days")
            
            st.write("---")
            
            # School schedule input
            st.write("### 🏫 Your School Schedule")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Weekdays**")
                weekday_start = st.time_input("School Start Time (Weekdays)", value=datetime.strptime("06:30", "%H:%M").time(), key="weekday_start")
                weekday_end = st.time_input("School End Time (Weekdays)", value=datetime.strptime("19:00", "%H:%M").time(), key="weekday_end")
            
            with col2:
                st.write("**Weekends**")
                weekend_schedule = st.radio("Weekend Schedule", 
                                           ["Full day available", "Half day (morning)", "Half day (afternoon)"],
                                           key="weekend_sched")
            
            # Generate button
            if st.button("🚀 Generate My Complete Schedule", type="primary"):
                st.write("---")
                st.success("✅ Your Personalized Schedule Generated!")
                
                # Determine dietary goal based on body type and BMI
                if latest_bmi < 18.5:
                    diet_goal = "Muscle Gain"
                    calorie_target = 2500
                elif latest_bmi >= 25:
                    diet_goal = "Weight Loss"
                    calorie_target = 1800
                else:
                    diet_goal = "Maintenance"
                    calorie_target = 2200
                
                # Calculate optimal sleep schedule
                if sleep_week:
                    avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_week]) / len(sleep_week)
                    # Recommend 8-9 hours
                    recommended_sleep = 8.5 if avg_sleep < 8 else 9
                else:
                    recommended_sleep = 8.5
                
                # Calculate bedtime based on school start
                wake_time = weekday_start
                sleep_hours = int(recommended_sleep)
                sleep_minutes = int((recommended_sleep - sleep_hours) * 60)
                
                # Calculate bedtime
                wake_datetime = datetime.combine(datetime.today(), wake_time)
                bedtime_datetime = wake_datetime - timedelta(hours=sleep_hours, minutes=sleep_minutes)
                bedtime = bedtime_datetime.time()
                
                # Create schedule tabs
                schedule_tab1, schedule_tab2, schedule_tab3 = st.tabs(["📅 Weekly Schedule", "🍽️ Diet Plan", "💤 Sleep Schedule"])
                
                with schedule_tab1:
                    st.subheader("Your Weekly Workout Schedule")
                    
                    # Determine workout frequency based on NAPFA scores
                    weak_areas = [test for test, grade in latest_napfa['grades'].items() if grade < 3]
                    workout_days = 5 if len(weak_areas) >= 3 else 4
                    
                    # Generate weekly schedule
                    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                    weekend = ["Saturday", "Sunday"]
                    
                    # Calculate workout times
                    school_end_time = datetime.combine(datetime.today(), weekday_end)
                    workout_start = school_end_time + timedelta(hours=1)  # 1 hour after school
                    
                    workout_schedule = []
                    
                    # Weekday workouts
                    days_with_workout = weekdays[:workout_days] if workout_days <= 5 else weekdays
                    
                    for idx, day in enumerate(weekdays):
                        if day in days_with_workout:
                            # Rotate workout focus
                            if idx % 3 == 0:
                                focus = "Upper Body & Core"
                                duration = 45
                            elif idx % 3 == 1:
                                focus = "Lower Body & Cardio"
                                duration = 50
                            else:
                                focus = "NAPFA Training"
                                duration = 45
                            
                            workout_schedule.append({
                                'day': day,
                                'time': workout_start.strftime("%H:%M"),
                                'activity': focus,
                                'duration': duration,
                                'type': 'weekday'
                            })
                        else:
                            workout_schedule.append({
                                'day': day,
                                'time': '-',
                                'activity': 'Rest Day',
                                'duration': 0,
                                'type': 'weekday'
                            })
                    
                    # Weekend workouts
                    if weekend_schedule == "Full day available":
                        weekend_time = "09:00"
                    elif weekend_schedule == "Half day (morning)":
                        weekend_time = "07:00"
                    else:
                        weekend_time = "14:00"
                    
                    workout_schedule.append({
                        'day': 'Saturday',
                        'time': weekend_time,
                        'activity': 'Long Cardio / Sports',
                        'duration': 60,
                        'type': 'weekend'
                    })
                    
                    workout_schedule.append({
                        'day': 'Sunday',
                        'time': '-',
                        'activity': 'Active Recovery (Light walk/stretch)',
                        'duration': 30,
                        'type': 'weekend'
                    })
                    
                    # Display schedule
                    for item in workout_schedule:
                        if item['activity'] != 'Rest Day':
                            st.markdown(f"""
                            **{item['day']}** - {item['time']}  
                            🏋️ {item['activity']} ({item['duration']} min)
                            """)
                        else:
                            st.markdown(f"**{item['day']}** - Rest Day 😴")
                        st.write("")
                    
                    # Store for optional save
                    if 'generated_schedule' not in st.session_state:
                        st.session_state.generated_schedule = workout_schedule
                
                with schedule_tab2:
                    st.subheader("Your Personalized Diet Plan")
                    
                    st.write(f"**Goal:** {diet_goal}")
                    st.write(f"**Body Type:** {body_type} - {body_description}")
                    st.write(f"**Daily Calorie Target:** {calorie_target} kcal")
                    st.write("")
                    
                    # Generate meal plan based on body type and goal
                    if body_type == "Ectomorph":
                        st.write("**Nutrition Focus:** High calories, protein, complex carbs")
                        protein_target = "1.8-2.0g per kg bodyweight"
                        carb_focus = "High (50-60% of calories)"
                    elif body_type == "Mesomorph":
                        st.write("**Nutrition Focus:** Balanced macros, moderate calories")
                        protein_target = "1.5-1.8g per kg bodyweight"
                        carb_focus = "Moderate (40-50% of calories)"
                    else:  # Endomorph
                        st.write("**Nutrition Focus:** Controlled carbs, high protein")
                        protein_target = "1.5-2.0g per kg bodyweight"
                        carb_focus = "Lower (30-40% of calories)"
                    
                    st.write(f"**Protein Target:** {protein_target}")
                    st.write(f"**Carb Focus:** {carb_focus}")
                    st.write("")
                    
                    # Weekday meal plan
                    st.markdown("#### 📅 Weekday Meal Plan")
                    
                    st.markdown(f"""
                    **Breakfast** ({(weekday_start.hour - 1):02d}:00 - before school)
                    - Options: Oatmeal with fruits & nuts, Eggs with whole wheat toast, Protein smoothie
                    - Calories: ~500 kcal | Protein: ~20g
                    
                    **Mid-Morning Snack** (10:30 - during break)
                    - Options: Banana with peanut butter, Greek yogurt, Nuts & dried fruit
                    - Calories: ~200 kcal | Protein: ~10g
                    
                    **Lunch** (13:00)
                    - Options: Chicken rice, Fish with vegetables, Pasta with lean meat
                    - Calories: ~600 kcal | Protein: ~35g
                    
                    **Pre-Workout Snack** ({(weekday_end.hour):02d}:30 - before training)
                    - Options: Banana, Energy bar, Small sandwich
                    - Calories: ~200 kcal | Protein: ~10g
                    
                    **Post-Workout** ({(workout_start.hour + 1):02d}:00 - after training)
                    - Options: Chocolate milk, Protein shake with banana
                    - Calories: ~300 kcal | Protein: ~25g
                    
                    **Dinner** ({(workout_start.hour + 2):02d}:00)
                    - Options: Grilled chicken/fish with vegetables, Lean beef with sweet potato
                    - Calories: ~600 kcal | Protein: ~40g
                    
                    **Evening Snack** (Optional, 2hrs before bed)
                    - Options: Cottage cheese, Casein shake, Small fruit
                    - Calories: ~150 kcal | Protein: ~15g
                    """)
                    
                    st.write("")
                    st.markdown("#### 🎉 Weekend Meal Plan")
                    st.write("More flexible timing - maintain same portions and quality")
                    st.write("• Focus on whole foods")
                    st.write("• Stay hydrated (8-10 glasses water)")
                    st.write("• Limit processed foods and sugar")
                    
                    # Store diet plan
                    if 'generated_diet' not in st.session_state:
                        st.session_state.generated_diet = {
                            'goal': diet_goal,
                            'body_type': body_type,
                            'calories': calorie_target,
                            'protein_target': protein_target
                        }
                
                with schedule_tab3:
                    st.subheader("Optimized Sleep Schedule")
                    
                    st.write(f"**Recommended Sleep:** {recommended_sleep} hours")
                    st.write(f"**Current Average:** {avg_sleep:.1f} hours" if sleep_week else "No data")
                    st.write("")
                    
                    # Weekday sleep
                    st.markdown("#### 📅 Weekday Sleep Schedule")
                    st.write(f"🌙 **Bedtime:** {bedtime.strftime('%H:%M')}")
                    st.write(f"☀️ **Wake Time:** {wake_time.strftime('%H:%M')}")
                    st.write(f"⏰ **Sleep Duration:** {recommended_sleep} hours")
                    
                    st.write("")
                    st.write("**Pre-Sleep Routine (30 min before bed):**")
                    st.write("1. 📱 Put away all screens")
                    st.write("2. 🚿 Shower or wash up")
                    st.write("3. 📖 Light reading or relaxation")
                    st.write("4. 🧘 Deep breathing exercises")
                    
                    st.write("")
                    st.markdown("#### 🎉 Weekend Sleep Schedule")
                    weekend_bedtime = (bedtime_datetime + timedelta(hours=1)).time()
                    weekend_wake = (wake_datetime + timedelta(hours=1.5)).time()
                    
                    st.write(f"🌙 **Bedtime:** {weekend_bedtime.strftime('%H:%M')} (can be 1hr later)")
                    st.write(f"☀️ **Wake Time:** {weekend_wake.strftime('%H:%M')} (can sleep in 1.5hrs)")
                    st.write("**Tip:** Keep weekend schedule within 2 hours of weekday for consistency")
                    
                    st.write("")
                    st.write("**Sleep Quality Tips:**")
                    st.write("✅ Keep room cool (18-20°C)")
                    st.write("✅ Complete darkness or eye mask")
                    st.write("✅ No caffeine after 2 PM")
                    st.write("✅ Exercise earlier in day (not close to bedtime)")
                    st.write("✅ Same schedule daily (including weekends)")
                
                # Option to save to schedule
                st.write("---")
                if st.button("💾 Save Workout Schedule to Training Tab", type="primary"):
                    # Save to user's schedule
                    for item in workout_schedule:
                        if item['activity'] not in ['Rest Day', 'Active Recovery (Light walk/stretch)']:
                            user_data['schedule'].append({
                                'day': item['day'],
                                'activity': item['activity'],
                                'time': item['time'],
                                'duration': item['duration']
                            })
                    
                    update_user_data(user_data)
                    st.success("✅ Schedule saved to Training Schedule tab!")
                    st.balloons()
    
    with tab2:
        st.subheader("🍳 Healthy Recipe Database")
        st.write("Browse recipes tailored to your dietary goals!")
        
        # Filter by diet goal
        if 'generated_diet' in st.session_state:
            default_goal = st.session_state.generated_diet['goal']
        else:
            default_goal = "Maintenance"
        
        selected_diet = st.selectbox(
            "Select Dietary Goal",
            ["Weight Loss", "Muscle Gain", "Maintenance"],
            index=["Weight Loss", "Muscle Gain", "Maintenance"].index(default_goal)
        )
        
        # Get recipes
        recipes_dict = search_recipes_by_diet(selected_diet)
        recipes = recipes_dict.get(selected_diet, [])
        
        if recipes:
            st.write(f"**Found {len(recipes)} recipes for {selected_diet}**")
            st.write("")
            
            # Display recipes
            for idx, recipe in enumerate(recipes):
                with st.expander(f"🍽️ {recipe['name']} - {recipe['calories']} kcal", expanded=(idx == 0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Nutritional Info:**")
                        st.write(f"- Calories: {recipe['calories']} kcal")
                        st.write(f"- Protein: {recipe['protein']}")
                        st.write(f"- Carbs: {recipe['carbs']}")
                        st.write(f"- Prep Time: {recipe['prep_time']}")
                    
                    with col2:
                        st.write("**Meal Type:**")
                        if recipe['calories'] < 300:
                            st.write("🥗 Snack/Light meal")
                        elif recipe['calories'] < 450:
                            st.write("🍽️ Main meal")
                        else:
                            st.write("🍖 Post-workout meal")
                    
                    st.write("")
                    st.write("**Ingredients:**")
                    for ingredient in recipe['ingredients']:
                        st.write(f"• {ingredient}")
                    
                    st.write("")
                    st.write("**Instructions:**")
                    st.write(recipe['instructions'])
        else:
            st.info("No recipes found. Select a dietary goal above.")
        
        st.write("---")
        st.info("💡 **Tip:** These recipes align with your body type and fitness goals. Mix and match to create variety in your diet!")
    
    with tab3:
        st.subheader("💬 Chat with Your AI Fitness Assistant")
        st.write("Ask me anything about fitness, nutrition, training, or your progress!")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat interface
        user_question = st.text_input("Ask your question:", placeholder="e.g., How can I improve my pull-ups?", key="chat_input")
        
        if st.button("Send", key="send_chat"):
            if user_question:
                # Add user question to history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Generate AI response based on user data and question
                ai_response = generate_ai_response(user_question, user_data)
                
                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Display chat history
        if st.session_state.chat_history:
            st.write("---")
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 AI Coach:** {message['content']}")
                st.write("")
        
        # Quick question buttons
        st.write("---")
        st.write("**Quick Questions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("How to improve cardio?", key="q1"):
                st.session_state.chat_history.append({"role": "user", "content": "How can I improve my cardio?"})
                response = "To improve cardio: (1) Start with 20-30 min runs 3x/week, (2) Add interval training (sprint 1 min, jog 2 min), (3) Gradually increase distance by 10% weekly, (4) Mix running with swimming/cycling, (5) Track your heart rate - aim for 60-80% max HR for endurance!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("Best recovery foods?", key="q2"):
                st.session_state.chat_history.append({"role": "user", "content": "What are the best recovery foods?"})
                response = "Best post-workout recovery foods: (1) Chocolate milk (protein + carbs), (2) Greek yogurt with berries, (3) Banana with peanut butter, (4) Grilled chicken with sweet potato, (5) Salmon with quinoa. Eat within 30-60 minutes after exercise for best recovery!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("Prevent injuries?", key="q3"):
                st.session_state.chat_history.append({"role": "user", "content": "How do I prevent injuries?"})
                response = "Injury prevention tips: (1) Always warm up 5-10 min before exercise, (2) Cool down and stretch after workouts, (3) Increase training intensity gradually, (4) Rest at least 1-2 days/week, (5) Listen to your body - pain is a warning sign, (6) Stay hydrated, (7) Wear proper shoes for your activity!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with tab2:
        st.subheader("📋 Generate Custom Workout Plan")
        st.write("Get a personalized workout plan based on your schedule and goals!")
        
        # Workout plan preferences
        st.write("### Your Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            days_available = st.multiselect(
                "Available Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Wednesday", "Friday"]
            )
        
        with col2:
            session_duration = st.selectbox(
                "Session Duration",
                ["30 minutes", "45 minutes", "60 minutes", "90 minutes"],
                index=2
            )
        
        workout_location = st.selectbox(
            "Workout Location",
            ["Home (no equipment)", "Home (basic equipment)", "Gym", "Outdoor/Park", "School"]
        )
        
        primary_goal = st.selectbox(
            "Primary Goal",
            ["Improve NAPFA scores", "Build strength", "Increase endurance", "Lose weight", "Gain muscle", "General fitness"]
        )
        
        fitness_level = st.selectbox(
            "Current Fitness Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        # Generate button
        if st.button("Generate My Custom Plan", type="primary"):
            st.write("---")
            st.success("✅ Your Personalized Workout Plan")
            
            # Generate plan based on inputs
            duration_min = int(session_duration.split()[0])
            
            st.write(f"**Schedule:** {len(days_available)} days per week")
            st.write(f"**Duration:** {session_duration} per session")
            st.write(f"**Location:** {workout_location}")
            st.write(f"**Goal:** {primary_goal}")
            st.write("")
            
            # Generate day-by-day plan
            for idx, day in enumerate(days_available):
                with st.expander(f"📅 {day} - {session_duration}", expanded=True):
                    # Vary the workout focus
                    if len(days_available) >= 4:
                        if idx % 4 == 0:
                            focus = "Upper Body Strength"
                        elif idx % 4 == 1:
                            focus = "Lower Body & Core"
                        elif idx % 4 == 2:
                            focus = "Cardio & Endurance"
                        else:
                            focus = "Full Body & Flexibility"
                    elif len(days_available) >= 3:
                        if idx % 3 == 0:
                            focus = "Strength Training"
                        elif idx % 3 == 1:
                            focus = "Cardio Training"
                        else:
                            focus = "Full Body"
                    else:
                        focus = "Full Body Workout"
                    
                    st.markdown(f"**Focus:** {focus}")
                    
                    # Generate exercises based on location and focus
                    exercises = generate_workout_exercises(focus, workout_location, duration_min, fitness_level)
                    
                    st.write("**Warm-up (5-10 min):**")
                    st.write("- Light jogging or jumping jacks: 3 minutes")
                    st.write("- Dynamic stretches: 5 minutes")
                    st.write("- Arm circles, leg swings, hip rotations")
                    
                    st.write("")
                    st.write("**Main Workout:**")
                    for exercise in exercises:
                        st.write(f"- {exercise}")
                    
                    st.write("")
                    st.write("**Cool-down (5-10 min):**")
                    st.write("- Easy walk/jog: 3 minutes")
                    st.write("- Static stretches: Hold each 30 seconds")
                    st.write("- Focus on muscles worked today")
            
            # Additional tips
            st.write("---")
            st.write("### 💡 Training Tips")
            st.write("✅ **Progression:** Increase weight/reps by 5-10% every 2 weeks")
            st.write("✅ **Rest:** Take 1-2 rest days between intense sessions")
            st.write("✅ **Hydration:** Drink water before, during, and after workouts")
            st.write("✅ **Nutrition:** Eat protein + carbs within 1 hour post-workout")
            st.write("✅ **Sleep:** Get 8-10 hours for optimal recovery")
            st.write("✅ **Listen to your body:** Rest if you feel pain (not soreness)")
            
            # Track in schedule
            if st.button("💾 Save This Workout Plan", type="primary"):
                # Save the entire workout plan
                user_data['saved_workout_plan'] = {
                    'days': days_available,
                    'duration': session_duration,
                    'location': workout_location,
                    'goal': primary_goal,
                    'level': fitness_level,
                    'created_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Also add to schedule
                for day in days_available:
                    user_data['schedule'].append({
                        'day': day,
                        'activity': f"Custom Workout - {primary_goal}",
                        'time': "To be scheduled",
                        'duration': duration_min
                    })
                
                update_user_data(user_data)
                st.success("✅ Workout plan saved! Check 'My Saved Plan' and 'Training Schedule' tabs.")
                st.rerun()
        
        # Display saved workout plan if exists
        if 'saved_workout_plan' in user_data and user_data['saved_workout_plan']:
            st.write("---")
            st.subheader("📌 Your Saved Workout Plan")
            saved = user_data['saved_workout_plan']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Days/Week", len(saved['days']))
            with col2:
                st.metric("Duration", saved['duration'])
            with col3:
                st.metric("Created", saved['created_date'])
            
            st.write(f"**Goal:** {saved['goal']}")
            st.write(f"**Location:** {saved['location']}")
            st.write(f"**Days:** {', '.join(saved['days'])}")
            
            if st.button("🗑️ Delete Saved Plan"):
                user_data['saved_workout_plan'] = None
                update_user_data(user_data)
                st.rerun()
    
    with tab3:
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

# Reminders and Progress
def reminders_and_progress():
    st.header("📊 Weekly Progress Report")
    
    user_data = get_user_data()
    
    # Reminder Bar at the top
    st.markdown("### 🔔 Today's Reminders")
    
    today = datetime.now().strftime('%A')
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Check scheduled activities for today
    today_activities = [s for s in user_data.get('schedule', []) if s['day'] == today]
    
    if today_activities:
        for activity in today_activities:
            st.info(f"⏰ **Today:** {activity['activity']} - {activity['time']} ({activity['duration']} min)")
    else:
        st.success(f"✅ No workouts scheduled for {today}. Good rest day or add a session!")
    
    # Smart reminders based on data
    reminders = []
    
    # Check last NAPFA test
    if user_data.get('napfa_history'):
        last_napfa_date = datetime.strptime(user_data['napfa_history'][-1]['date'], '%Y-%m-%d')
        days_since_napfa = (datetime.now() - last_napfa_date).days
        if days_since_napfa > 30:
            reminders.append(f"📝 It's been {days_since_napfa} days since your last NAPFA test. Consider retesting to track progress!")
    
    # Check last BMI
    if user_data.get('bmi_history'):
        last_bmi_date = datetime.strptime(user_data['bmi_history'][-1]['date'], '%Y-%m-%d')
        days_since_bmi = (datetime.now() - last_bmi_date).days
        if days_since_bmi > 14:
            reminders.append(f"⚖️ Update your BMI - last recorded {days_since_bmi} days ago")
    
    # Check sleep tracking
    if user_data.get('sleep_history'):
        last_sleep_date = datetime.strptime(user_data['sleep_history'][-1]['date'], '%Y-%m-%d')
        if last_sleep_date.strftime('%Y-%m-%d') != today_date:
            reminders.append("😴 Don't forget to log your sleep from last night!")
    else:
        reminders.append("😴 Start tracking your sleep for better recovery insights!")
    
    # Check exercise logging
    if user_data.get('exercises'):
        last_exercise_date = datetime.strptime(user_data['exercises'][0]['date'], '%Y-%m-%d')
        days_since_exercise = (datetime.now() - last_exercise_date).days
        if days_since_exercise > 2:
            reminders.append(f"💪 It's been {days_since_exercise} days since your last logged workout. Time to get moving!")
    else:
        reminders.append("💪 Start logging your exercises to track your fitness journey!")
    
    # Check goals progress
    if user_data.get('goals'):
        for goal in user_data['goals']:
            target_date = datetime.strptime(goal['date'], '%Y-%m-%d')
            days_until = (target_date - datetime.now()).days
            if 0 <= days_until <= 7:
                reminders.append(f"🎯 Goal deadline approaching: '{goal['target']}' in {days_until} days!")
    
    if reminders:
        st.markdown("### 💡 Smart Reminders")
        for reminder in reminders:
            st.warning(reminder)
    
    st.write("---")
    
    # Weekly Progress Report
    st.markdown("### 📈 Your Weekly Summary")
    
    # Calculate date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏃 NAPFA Progress", "💪 Exercise Stats", "😴 Sleep Analysis"])
    
    with tab1:
        st.subheader("This Week at a Glance")
        
        # Count activities this week
        exercises_this_week = [e for e in user_data.get('exercises', []) 
                              if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
        
        sleep_this_week = [s for s in user_data.get('sleep_history', []) 
                          if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Workouts Logged", len(exercises_this_week))
        with col2:
            if exercises_this_week:
                total_mins = sum([e['duration'] for e in exercises_this_week])
                st.metric("Total Exercise", f"{total_mins} min")
            else:
                st.metric("Total Exercise", "0 min")
        with col3:
            st.metric("Sleep Tracked", len(sleep_this_week))
        with col4:
            if sleep_this_week:
                avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_this_week]) / len(sleep_this_week)
                st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
            else:
                st.metric("Avg Sleep", "No data")
        
        # All-time stats
        st.write("")
        st.markdown("#### 📚 All-Time Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Workouts", len(user_data.get('exercises', [])))
        with col2:
            st.metric("NAPFA Tests", len(user_data.get('napfa_history', [])))
        with col3:
            st.metric("BMI Records", len(user_data.get('bmi_history', [])))
        with col4:
            st.metric("Active Goals", len(user_data.get('goals', [])))
        
        # Workout consistency
        if user_data.get('exercises'):
            st.write("")
            st.markdown("#### 🔥 Workout Consistency")
            
            # Get unique workout dates
            workout_dates = list(set([e['date'] for e in user_data.get('exercises', [])]))
            workout_dates.sort(reverse=True)
            
            if len(workout_dates) >= 2:
                # Calculate streak
                streak = 1
                current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')
                
                for i in range(1, len(workout_dates)):
                    prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                    diff = (current_date - prev_date).days
                    
                    if diff <= 2:  # Allow 1 rest day
                        streak += 1
                        current_date = prev_date
                    else:
                        break
                
                if streak >= 3:
                    st.success(f"🔥 {streak} day streak! Keep it up!")
                else:
                    st.info(f"Current streak: {streak} days. Aim for 3+ for consistency!")
    
    with tab2:
        st.subheader("🏃 NAPFA Performance")
        
        if not user_data.get('napfa_history'):
            st.info("No NAPFA tests recorded yet. Complete your first test to track progress!")
        else:
            napfa_data = user_data['napfa_history']
            
            # Show latest scores
            latest = napfa_data[-1]
            st.write(f"**Latest Test:** {latest['date']}")
            st.write(f"**Total Score:** {latest['total']} points")
            st.write(f"**Medal:** {latest['medal']}")
            
            # Show grades breakdown
            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }
            
            st.write("")
            st.write("**Grade Breakdown:**")
            
            grades_df = pd.DataFrame([
                {
                    'Test': test_names[test],
                    'Score': latest['scores'][test],
                    'Grade': grade
                }
                for test, grade in latest['grades'].items()
            ])
            
            st.dataframe(grades_df, use_container_width=True, hide_index=True)
            
            # Progress over time
            if len(napfa_data) > 1:
                st.write("")
                st.write("**Progress Over Time:**")
                
                df = pd.DataFrame([
                    {'Date': test['date'], 'Total Score': test['total']}
                    for test in napfa_data
                ])
                df = df.set_index('Date')
                st.line_chart(df)
                
                # Calculate improvement
                first_score = napfa_data[0]['total']
                latest_score = napfa_data[-1]['total']
                improvement = latest_score - first_score
                
                if improvement > 0:
                    st.success(f"📈 You've improved by {improvement} points since your first test!")
                elif improvement < 0:
                    st.warning(f"📉 Score decreased by {abs(improvement)} points. Review your training plan.")
                else:
                    st.info("Score unchanged. Time to push harder!")
    
    with tab3:
        st.subheader("💪 Exercise Statistics")
        
        if not user_data.get('exercises'):
            st.info("No exercises logged yet. Start logging your workouts!")
        else:
            exercises = user_data['exercises']
            
            # Total stats
            total_workouts = len(exercises)
            total_minutes = sum([e['duration'] for e in exercises])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Workouts", total_workouts)
            with col2:
                st.metric("Total Time", f"{total_minutes} min ({total_minutes/60:.1f} hrs)")
            
            # Exercise frequency
            st.write("")
            st.write("**Exercise Frequency:**")
            exercise_counts = {}
            for ex in exercises:
                exercise_counts[ex['name']] = exercise_counts.get(ex['name'], 0) + 1
            
            df_chart = pd.DataFrame({
                'Exercise': list(exercise_counts.keys()),
                'Count': list(exercise_counts.values())
            }).sort_values('Count', ascending=False)
            
            df_chart = df_chart.set_index('Exercise')
            st.bar_chart(df_chart)
            
            # Intensity breakdown
            st.write("")
            st.write("**Intensity Distribution:**")
            intensity_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            for ex in exercises:
                intensity_counts[ex['intensity']] += 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Low Intensity", intensity_counts['Low'])
            with col2:
                st.metric("Medium Intensity", intensity_counts['Medium'])
            with col3:
                st.metric("High Intensity", intensity_counts['High'])
            
            # Recent workouts
            st.write("")
            st.write("**Recent Workouts:**")
            recent = exercises[:5]  # Last 5
            for ex in recent:
                st.write(f"• {ex['date']}: {ex['name']} - {ex['duration']}min ({ex['intensity']} intensity)")
    
    with tab4:
        st.subheader("😴 Sleep Analysis")
        
        if not user_data.get('sleep_history'):
            st.info("No sleep data yet. Start tracking your sleep!")
        else:
            sleep_data = user_data['sleep_history']
            
            # Calculate stats
            total_records = len(sleep_data)
            avg_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / total_records
            
            quality_counts = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0}
            for s in sleep_data:
                quality_counts[s['quality']] += 1
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sleep", f"{avg_hours:.1f} hours")
            with col2:
                st.metric("Records Tracked", total_records)
            
            # Quality breakdown
            st.write("")
            st.write("**Sleep Quality Distribution:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("😊 Excellent", quality_counts['Excellent'])
            with col2:
                st.metric("👍 Good", quality_counts['Good'])
            with col3:
                st.metric("😐 Fair", quality_counts['Fair'])
            with col4:
                st.metric("😴 Poor", quality_counts['Poor'])
            
            # Sleep trend
            if len(sleep_data) > 1:
                st.write("")
                st.write("**Sleep Duration Trend:**")
                df = pd.DataFrame(sleep_data)
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                df_chart = df.set_index('date')['total_hours']
                st.line_chart(df_chart)
            
            # Sleep insights
            st.write("")
            st.write("**Insights:**")
            if avg_hours >= 8:
                st.success("✅ Excellent sleep habits! Keep it up for optimal recovery and performance.")
            elif avg_hours >= 7:
                st.info("👍 Good sleep duration. Try to get closer to 8-10 hours for peak performance.")
            else:
                st.warning("⚠️ You're not getting enough sleep. Aim for 8-10 hours for teenagers!")
            
            # Best and worst
            if len(sleep_data) >= 3:
                sleep_sorted = sorted(sleep_data, key=lambda x: x['hours'] + x['minutes']/60, reverse=True)
                best = sleep_sorted[0]
                worst = sleep_sorted[-1]
                
                st.write(f"**Best night:** {best['date']} - {best['hours']}h {best['minutes']}m")
                st.write(f"**Shortest night:** {worst['date']} - {worst['hours']}h {worst['minutes']}m")

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
                           ["📊 Weekly Progress", "🤖 AI Insights", "BMI Calculator", "NAPFA Test", "Sleep Tracker", 
                            "Exercise Log", "Set Goals", "Training Schedule"])
    
    # Display selected page
    if page == "📊 Weekly Progress":
        reminders_and_progress()
    elif page == "🤖 AI Insights":
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
