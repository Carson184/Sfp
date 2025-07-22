import streamlit as st
import requests
import random

st.set_page_config(page_title="Nutrition Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner with 🧬 Nutrition Data")

API_KEY = "14f2e049c4d54a5caa6ccd6e8c9718d6" 

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
meal_types = [("B", "Breakfast"), ("L", "Lunch"), ("D", "Dinner")]

# Initialize session state
for d in days:
    for code, _ in meal_types:
        key = f"{d}_{code}"
        if key not in st.session_state:
            st.session_state[key] = {"name": "", "cal": "", "protein": "", "carbs": "", "fat": ""}
        if f"suggestions_{key}" not in st.session_state:
            st.session_state[f"suggestions_{key}"] = []

# Spoonacular recipe search
def search_recipes(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": query,
        "number": 6,
        "addRecipeNutrition": True
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json().get("results", [])

# Generate random meals from search terms
def generate_all():
    for d in days:
        for code, label in meal_types:
            results = search_recipes(label)
            if results:
                recipe = random.choice(results)
                fill_meal(d, code, recipe)

# Fill meal slot
def fill_meal(day, code, data):
    key = f"{day}_{code}"
    st.session_state[key] = {
        "name": data["title"],
        "cal": f'{int(data["nutrition"]["nutrients"][0]["amount"])} kcal',
        "protein": f'{data["nutrition"]["nutrients"][1]["amount"]}g',
        "fat": f'{data["nutrition"]["nutrients"][2]["amount"]}g',
        "carbs": f'{data["nutrition"]["nutrients"][3]["amount"]}g'
    }

# 📌 Search Box
st.subheader("🔍 Search Meals")
search_term = st.text_input("Enter a food keyword (e.g. 'curry', 'salad', 'pasta')")

selected_day = st.selectbox("Select day to apply result:", days)
selected_meal = st.selectbox("Select meal type:", [label for _, label in meal_types])

if search_term:
    try:
        found = search_recipes(search_term)
        if found:
            st.write(f"**Found {len(found)} results:**")
            for recipe in found:
                col = st.columns([3, 1])
                with col[0]:
                    st.write(f"- {recipe['title']}")
                    nutr = recipe["nutrition"]["nutrients"]
                    st.caption(f"Calories: {int(nutr[0]['amount'])} kcal | Protein: {nutr[1]['amount']}g | Carbs: {nutr[3]['amount']}g | Fat: {nutr[2]['amount']}g")
                with col[1]:
                    if st.button("Use this", key=f"fill_{recipe['id']}"):
                        code = [c for c, l in meal_types if l == selected_meal][0]
                        fill_meal(selected_day, code, recipe)
        else:
            st.warning("No matches found.")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.button("🎲 Generate All Meals", on_click=generate_all)

# 📝 Weekly Planner
st.subheader("📋 Plan Your Week")

for day in days:
    st.write(f"### {day}")
    cols = st.columns(3)
    for i, (code, label) in enumerate(meal_types):
        key = f"{day}_{code}"
        with cols[i]:
            st.write(f"**{label}**")
            meal = st.session_state[key]
            st.text_input("Meal", value=meal["name"], key=f"{key}_name", disabled=True)
            st.caption(f"Calories: {meal['cal']} | Protein: {meal['protein']} | Carbs: {meal['carbs']} | Fat: {meal['fat']}")

# 📅 Summary
st.markdown("---")
st.subheader("📊 Weekly Summary")

for day in days:
    b = st.session_state[f"{day}_B"]
    l = st.session_state[f"{day}_L"]
    d = st.session_state[f"{day}_D"]
    st.write(f"**{day}**")
    st.markdown(f"- 🍳 **Breakfast**: {b['name']} ({b['cal']})")
    st.markdown(f"- 🍱 **Lunch**: {l['name']} ({l['cal']})")
    st.markdown(f"- 🍲 **Dinner**: {d['name']} ({d['cal']})")
