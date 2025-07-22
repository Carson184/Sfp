import streamlit as st
import random

st.set_page_config(page_title="🍽️ Meal Planner", layout="wide")
st.title("🍴 Advanced Meal Planner")

# 1. Period selection
period = st.radio("Choose planning period:", ["Weekly", "Monthly"])
if period == "Weekly":
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
else:
    days = [f"Day {i}" for i in range(1, 31)]

# 2. Cuisine selection
cuisines = {
    "Italian": [
        "Spaghetti Bolognese", "Margherita Pizza", "Risotto with Mushrooms",
        "Caprese Salad", "Bruschetta", "Lasagna"
    ],
    "Chinese": [
        "Kung Pao Chicken", "Mapo Tofu", "Sweet & Sour Pork",
        "Vegetable Chow Mein", "Chicken Fried Rice", "Dumplings"
    ],
    "Indian": [
        "Butter Chicken", "Chana Masala", "Palak Paneer",
        "Vegetable Biryani", "Dal Tadka", "Aloo Gobi"
    ],
    "Mexican": [
        "Beef Tacos", "Chicken Quesadilla", "Veggie Burrito",
        "Enchiladas", "Guacamole & Chips", "Chilaquiles"
    ],
    "Japanese": [
        "Sushi Rolls", "Ramen", "Miso Soup & Rice",
        "Teriyaki Chicken", "Tempura Vegetables", "Onigiri"
    ]
}
all_cuisines = ["Random"] + list(cuisines.keys())
choice = st.selectbox("Select a cuisine for suggestions:", all_cuisines)

# 3. Prepare session state
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {day: "" for day in days}

# Helper to pick a meal
def pick_meal():
    if choice == "Random":
        cuisine = random.choice(list(cuisines.keys()))
    else:
        cuisine = choice
    return random.choice(cuisines[cuisine])

# 4. Global generate button
if st.button("🎲 Generate All Meals"):
    for day in days:
        st.session_state.meal_plan[day] = pick_meal()

# 5. Layout inputs & Suggest buttons
st.subheader("📝 Plan Your Meals")
for day in days:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.session_state.meal_plan[day] = st.text_input(
            f"{day}:", st.session_state.meal_plan[day], key=day
        )
    with col2:
        if st.button("Suggest", key=f"suggest_{day}"):
            st.session_state.meal_plan[day] = pick_meal()

# 6. Display summary
st.subheader("📅 Your Meal Schedule")
for day, meal in st.session_state.meal_plan.items():
    status = meal if meal else "Not planned yet"
    st.write(f"**{day}**: {status}")


# Summary display
st.subheader("📅 Your Meal Schedule")
for day, meal in st.session_state.meal_plan.items():
    st.write(f"**{day}**: {meal if meal else 'Not planned yet'}")
