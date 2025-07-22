import streamlit as st
import random

st.title("🍽️ Simple Weekly Meal Planner")

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# Simple meal lists
breakfasts = ["Oatmeal & Berries","Yogurt Parfait","Avocado Toast","Smoothie Bowl"]
lunches    = ["Grilled Chicken Salad","Veggie Wrap","Quinoa Bowl","Sushi Roll"]
dinners    = ["Salmon & Veggies","Stir-Fry Tofu","Beef Tacos","Pasta Primavera"]

# Keep plan in session
if "plan" not in st.session_state:
    st.session_state.plan = {day: {"B": "","L": "","D": ""} for day in days}

# Helper to pick a random meal by type
def suggest(day, meal_type):
    lists = {"B": breakfasts, "L": lunches, "D": dinners}
    st.session_state.plan[day][meal_type] = random.choice(lists[meal_type])

st.subheader("Plan Your Week")
for day in days:
    st.write(f"**{day}**")
    cols = st.columns([3,1,3,1,3,1])
    # Breakfast
    with cols[0]:
        st.text_input("Breakfast", key=f"{day}_B", value=st.session_state.plan[day]["B"])
    with cols[1]:
        if st.button("Suggest", key=f"sugg_{day}_B"):
            suggest(day, "B")
    # Lunch
    with cols[2]:
        st.text_input("Lunch", key=f"{day}_L", value=st.session_state.plan[day]["L"])
    with cols[3]:
        if st.button("Suggest", key=f"sugg_{day}_L"):
            suggest(day, "L")
    # Dinner
    with cols[4]:
        st.text_input("Dinner", key=f"{day}_D", value=st.session_state.plan[day]["D"])
    with cols[5]:
        if st.button("Suggest", key=f"sugg_{day}_D"):
            suggest(day, "D")

# Show summary
st.markdown("---")
st.subheader("📅 Your Plan")
for day in days:
    b = st.session_state.plan[day]["B"] or "–"
    l = st.session_state.plan[day]["L"] or "–"
    d = st.session_state.plan[day]["D"] or "–"
    st.write(f"**{day}** • Breakfast: {b}  |  Lunch: {l}  |  Dinner: {d}")
