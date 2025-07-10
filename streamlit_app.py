# Import packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title and Input
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get Snowflake session
session = get_active_session()

# Get fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Multiselect input (up to 5 fruits)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# Checkbox to mark order as filled
order_filled = st.checkbox('Mark order as filled?')

if ingredients_list:
    # Show nutrition info
    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"Could not get info for {fruit_chosen}")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    # Prepare SQL insert
    ingredients_string = ', '.join(ingredients_list)  # comma separated list
    filled_status = 'TRUE' if order_filled else 'FALSE'

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
        VALUES ('{ingredients_string}', '{name_on_order}', {filled_status})
    """

    st.write("SQL to be executed:")
    st.code(my_insert_stmt)

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

#New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

