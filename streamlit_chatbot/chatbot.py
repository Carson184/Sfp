import os
import requests

EDAMAM_ID = os.getenv("EDAMAM_ID")
EDAMAM_KEY = os.getenv("EDAMAM_KEY")
SPOON_API_KEY = os.getenv("SPOON_API_KEY")

def get_nutrition(ingredients: str) -> dict:
    """
    ingredients: comma-separated items, e.g. "1 apple, 2 eggs"
    Returns full nutrition JSON (calories, macros, vitamins…)
    """
    url = "https://api.edamam.com/api/nutrition-details"
    body = {"ingr": [i.strip() for i in ingredients.split(",")]}
    params = {"app_id": EDAMAM_ID, "app_key": EDAMAM_KEY}
    resp = requests.post(url, json=body, params=params)
    resp.raise_for_status()
    return resp.json()

def search_recipes(query: str, cuisine: str = None, diet: str = None) -> list:
    """
    Returns up to 20 recipes matching query + optional filters.
    """
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": SPOON_API_KEY,
        "query": query,
        "number": 20,
        **({"cuisine": cuisine} if cuisine else {}),
        **({"diet": diet} if diet else {})
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("results", [])
import streamlit as st
import pandas as pd
import sqlite3
import random
from nutrition_client import get_nutrition, search_recipes

# --- Database Setup ---
conn = sqlite3.connect("meal_plans.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
  CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY,
    date TEXT,
    meal_type TEXT,
    items TEXT,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL
  )
""")
conn.commit()

# --- Streamlit Config ---
st.set_page_config(page_title="Meal Planner Pro+", layout="wide")
st.title("🍴 Meal Planner Pro+")

# --- Sidebar Controls ---
view   = st.sidebar.radio("View:", ["Plan Meals", "Search Recipes", "My Plans"])
period = st.sidebar.selectbox("Period:", ["Weekly", "Monthly"])
cuisine = st.sidebar.selectbox(
  "Cuisine:", ["Random", "Italian", "Chinese", "Indian", "Mexican"]
)
diet = st.sidebar.multiselect(
  "Diet Filters:", ["Vegetarian", "Vegan", "Gluten-Free", "Keto"]
)

# Generate date list
days = pd.date_range(
  start=pd.Timestamp.today(), 
  periods=7 if period=="Weekly" else 30
).date

# --- Plan Meals View ---
if view == "Plan Meals":
    st.header("📋 Plan Your Meals")
    for date in days:
        st.subheader(str(date))
        cols = st.columns([3,1,2,1,2,1])
        for i, meal in enumerate(["Breakfast","Lunch","Dinner"]):
            key = f"{date}_{meal}"
            items = st.session_state.get(key, "")
            
            with cols[i*2]:
                items = st.text_input(f"{meal} items", key=key, value=items)
            
            with cols[i*2+1]:
                if st.button("Nutri Info", key=f"nutri_{key}"):
                    data = get_nutrition(items)
                    st.metric("Calories", f"{data['calories']} kcal")
                    macros = {
                      k: round(v["quantity"],1)
                      for k,v in data["totalNutrients"].items()
                      if k in ["CHOCDF","FAT","PROCNT"]
                    }
                    st.json(macros)
            
            if st.button("Suggest", key=f"suggest_{key}"):
                results = search_recipes(
                  meal.lower(),
                  None if cuisine=="Random" else cuisine,
                  ",".join(diet) if diet else None
                )
                if results:
                    choice = random.choice(results)
                    items = choice["title"]
                    st.session_state[key] = items
            
            if st.button("Save", key=f"save_{key}"):
                if items:
                    data = get_nutrition(items)
                    nutr = data["totalNutrients"]
                    cursor.execute("""
                      INSERT INTO plans
                      (date, meal_type, items, calories, protein, carbs, fat)
                      VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                      str(date), meal, items,
                      data["calories"],
                      nutr["PROCNT"]["quantity"],
                      nutr["CHOCDF"]["quantity"],
                      nutr["FAT"]["quantity"]
                    ))
                    conn.commit()
                    st.success("Saved!")

# --- Search Recipes View ---
elif view == "Search Recipes":
    st.header("🔍 Search Recipes")
    q = st.text_input("Search query:")
    if q:
        recs = search_recipes(q, None if cuisine=="Random" else cuisine, ",".join(diet) or None)
        for r in recs:
            st.write(f"**{r['title']}**")
            st.markdown(f"[View Recipe]({r.get('sourceUrl','')})")
            st.markdown("---")

# --- My Plans View ---
else:
    st.header("📂 My Saved Plans")
    df = pd.read_sql("SELECT * FROM plans", conn, parse_dates=["date"])
    st.dataframe(df)
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "my_meal_plans.csv")
