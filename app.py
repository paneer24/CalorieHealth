import streamlit as st
import os
import base64
import pandas as pd
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, image):
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input_prompt, image[0]])
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def parse_response(response_text):
    lines = response_text.strip().split('\n')
    items = [line.split(' - ') for line in lines if ' - ' in line]
    return items

def display_nutrition_details(response_text):
    items = parse_response(response_text)
    if items:
        df = pd.DataFrame(items, columns=["Food Item", "Calories"])
        st.table(df)
    else:
        st.error("Failed to parse the response.")

def create_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="nutrition_details.csv">Download CSV file</a>'
    return href

st.set_page_config(page_title="Gemini Image Demo")
st.header("Gemini Health App")

uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

input_prompt = """
    You are an expert nutritionist. You need to analyze the food items in the image
    and calculate the total calories. Provide the details of every food item with its calorie intake
    in the following format:

    1. Item 1 - number of calories
    2. Item 2 - number of calories
    ----
    ----
    Also, indicate if the food is healthy or not.
"""

submit = st.button("Tell me about the image")

if submit:
    for uploaded_file in uploaded_files:
        with st.spinner("Analyzing image..."):
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt, image_data)
            if response:
                st.subheader("The Response is")
                display_nutrition_details(response)
                items = parse_response(response)
                if items:
                    df = pd.DataFrame(items, columns=["Food Item", "Calories"])
                    st.markdown(create_csv_download_link(df), unsafe_allow_html=True)
