import streamlit as st
import random

# 🔧 Page Setup
st.set_page_config(page_title="Advanced Meal Planner", layout="wide")
st.title("🥗 Advanced Meal Planner")

# 📅 Days & Meals
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
meal_types = [("B", "Breakfast"), ("L", "Lunch"), ("D", "Dinner")]
default_tags = ["High Protein", "Low Carb", "Vegan", "Quick Prep", "Comfort Food"]

# 🧠 Initialize planner
for day in days:
    for code, _ in meal_types:
        key = f"{day}_{code}"
        if key not in st.session_state:
            st.session_state[key] = []

# 🔤 Format Meal Names
def format_title(name):
    return name.title()

# 🍽️ Add meals
def add_to_meal(day, code, data):
    key = f"{day}_{code}"
    if len(st.session_state[key]) >= 2:
        return
    if data.get("protein", 0) < 10:
        data["protein"] += 5
        data["cal"] += 20
    st.session_state[key].append({
        "name": format_title(data.get("title", "Untitled Meal")),
        "cal": data.get("cal", 0),
        "protein": data.get("protein", 0),
        "fat": data.get("fat", 0),
        "carbs": data.get("carbs", 0),
        "note": "",
        "tags": [],
        "rating": 1
    })

# 🍜 Recipe variety
def mock_recipes(meal_type):
    options = {
        "Breakfast": ["Avocado Toast", "Chia Seed Pudding", "Breakfast Burrito"],
        "Lunch": ["Grilled Chicken Salad", "Tofu Stir-Fry", "Falafel Wrap"],
        "Dinner": ["Shrimp Tacos", "Risotto", "Moroccan Chickpea Stew"],
        "fruit": ["Fruit Bowl", "Berry Smoothie Bowl", "Banana Chia Cups"]
    }
    titles = options.get(meal_type, [])
    sample_size = min(2, len(titles))
    meals = []
    for title in random.sample(titles, sample_size):
        cal = random.randint(280, 480)
        protein = round(cal * 0.25 / 4, 1)
        fat = round(cal * 0.25 / 9, 1)
        carbs = round((cal - (protein * 4 + fat * 9)) / 4, 1)
        meals.append({
            "title": title,
            "cal": cal,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        })
    return meals

# 📊 Macro visual
def show_macros(meals):
    p = sum(m["protein"] for m in meals)
    c = sum(m["carbs"] for m in meals)
    f = sum(m["fat"] for m in meals)
    total = p + c + f
    if total > 0:
        st.caption("Macro Split:")
        st.progress(p / total)
        st.caption(f"Protein: {round(p)}g")
        st.progress(c / total)
        st.caption(f"Carbs: {round(c)}g")
        st.progress(f / total)
        st.caption(f"Fat: {round(f)}g")

# 🧭 Goals
goal_calories = st.sidebar.number_input("🔢 Daily Calorie Goal", 1200, 5000, 1800)
goal_water = st.sidebar.number_input("💧 Water Goal (cups)", 0, 20, 8)
water = {day: st.sidebar.slider(f"{day} Water Intake", 0, 20, 8) for day in days}

# 🔍 Suggested Meals
st.subheader("🔎 Add a Suggested Meal")
col1, col2, col3 = st.columns(3)
query = col1.text_input("Meal Type")
sel_day = col2.selectbox("Day", days, key="search_day")
sel_meal = col3.selectbox("Meal", [label for _, label in meal_types], key="search_meal")

if query:
    for recipe in mock_recipes(query):
        st.write(f"**{format_title(recipe['title'])}**")
        st.caption(f"{recipe['cal']} kcal | Protein: {recipe['protein']}g | Carbs: {recipe['carbs']}g | Fat: {recipe['fat']}g")
        code = [c for c, l in meal_types if l == sel_meal][0]
        if st.button(f"+ Add {recipe['title']}", key=f"add_{recipe['title']}"):
            add_to_meal(sel_day, code, recipe)

# ✍️ Custom Entry
st.subheader("✍️ Add a Custom Meal")
cols = st.columns(5)
name = cols[0].text_input("Meal Name")
cal = cols[1].number_input("Calories", min_value=0)
p = cols[2].number_input("Protein", min_value=0.0)
c = cols[3].number_input("Carbs", min_value=0.0)
f = cols[4].number_input("Fat", min_value=0.0)
manual_day = st.selectbox("Day", days, key="manual_day")
manual_meal = st.selectbox("Meal", [label for _, label in meal_types], key="manual_meal")
if st.button("➕ Add Custom"):
    code = [c for c, l in meal_types if l == manual_meal][0]
    add_to_meal(manual_day, code, {
        "title": name,
        "cal": cal,
        "protein": p,
        "carbs": c,
        "fat": f
    })

# 🎲 Auto-Fill Week
st.markdown("---")
if st.button("🎲 Auto-Fill Week"):
    for day in days:
        for code, label in meal_types:
            pool = mock_recipes(label)
            if pool:
                add_to_meal(day, code, random.choice(pool))
            fruit_pool = mock_recipes("fruit")
            if fruit_pool:
                add_to_meal(day, code, random.choice(fruit_pool))

# 📋 Weekly Planner
st.subheader("📋 Weekly Planner")
for day in days:
    with st.expander(day):
        cols = st.columns(3)
        for i, (code, label) in enumerate(meal_types):
            key = f"{day}_{code}"
            with cols[i]:
                st.write(f"**{label}**")
                meals = st.session_state[key]
                total = sum(m["cal"] for m in meals)
                st.metric("Total Calories", f"{total} kcal")
                st.metric("Water Intake", f"{water[day]} cups")
                for idx, meal in enumerate(meals):
                    name = st.text_input("Meal", meal["name"], key=f"{key}_name_{idx}")
                    note = st.text_area("Notes", value=meal["note"], key=f"{key}_note_{idx}")
                    tags = st.multiselect("Tags", default_tags, default=meal["tags"], key=f"{key}_tags_{idx}")
                    rating = st.slider("Rating", 1, 5, value=meal["rating"], key=f"{key}_rating_{idx}")
                    meal["name"] = name
                    meal["note"] = note
                    meal["tags"] = tags
                    meal["rating"] = rating
                    st.caption(f"{meal['cal']} kcal | Protein: {meal['protein']}g | Carbs: {meal['carbs']}g | Fat: {meal['fat']}g")
                if total > 0:
                    show_macros(meals)
                if st.button(f"❌ Clear {label}", key=f"clear_{key}"):
                    st.session_state[key] = []

# 📊 Weekly Nutrition Summary
st.markdown("---")
st.subheader("📊 Weekly Nutrition Summary")

total_meals = 0
total_cals = 0
summary_lines = []

for day in days:
    all_meals = (
        st.session_state.get(f"{day}_B", []) +
        st.session_state.get(f"{day}_L", []) +
        st.session_state.get(f"{day}_D", [])
    )
    day_total = sum(m["cal"] for m in all_meals)
    total_meals += len(all_meals)
    total_cals += day_total
    summary_lines.append(f"{day}: {day_total} kcal across {len(all_meals)} meals")

st.write(f"**Total Weekly Calories:** {total_cals} kcal")
st.write(f"**Total Meals:** {total_meals}")
for line in summary_lines:
    st.caption(line)
