import time

import duckdb
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st

conn = duckdb.connect()

# dummy.csv refers to a file that I created with 100 million rows for testing.
# 3 gb dataset.

query = """
CREATE TABLE mytable AS
SELECT 
    column0 AS sepal_length,
    column1 AS sepal_width,
    column2 AS petal_length,
    column3 AS petal_width,
    column4 AS species
FROM read_csv_auto('iris/iris.data');
"""
# Creates table
conn.execute(query)

# Part 1: Testing with Duck DB show()
start_time = time.time()


query = """
select * 
from mytable
"""

shiw = conn.sql(query).show()
shiw
df = conn.sql(query).df()


print("--- %s seconds ---" % (time.time() - start_time))


st.title("Streamlit + duckdb Tutorial")
try:
    button = st.button(label="Check for a sample")
    if button:
        #  generate_dataset_orders(filename=filename, num_rows=1000)
        # load_file(db=db, infile_path=filename, table_name=destination_table_name)

        st.write("## Sample")
        st.dataframe(df.head(10), height=300)

    st.write("## Visualization")
    option = st.selectbox(
        "Select a dimension",
        ["sepal_length", "sepal_width", "petal_width", "petal_length"],
        key="option",
    )

    if option:
        option2 = st.selectbox(
            "Select another dimension",
            ["sepal_length", "sepal_width", "petal_width", "petal_length"],
            key="option2",
        )
        st.write(f"### Scatter Plot: {option} x {option2}")

        fig = px.scatter(
            df,
            x=option,
            y=option2,
            color="species",
            hover_name="species",
            log_x=True,
        )

        # Use the Streamlit theme.
        # This is the default. So you can also omit the theme argument.
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        # st.bar_chart(df, x=option, y="species")

        st.write(f"### Boxplot: {option} x Specices")
        fig, ax = plt.subplots()

        sns.boxplot(data=df, x="species", y=option, ax=ax)
        st.pyplot(fig)

        st.write("### Bar Chart: Species x Count")
        st.bar_chart(df["species"].value_counts())

    st.write("## Filters (by Species)")
    distinct_query = "SELECT DISTINCT species FROM mytable;"
    distinct_values = conn.execute(distinct_query).fetchall()

    # Convert results to a list of distinct values
    distinct_values_list = [value[0] for value in distinct_values]

    product_filter = st.selectbox(
        label="Select a specices", options=distinct_values_list, key="product_filter"
    )
    if product_filter != "--":
        query = (
            """
        select * from mytable where species = '"""
            + product_filter
            + """'
        """
        )

        result = conn.sql(query).df()
        st.dataframe(result.head(5))

        # To download the data we have just selected
        st.title("Boxplot Visualization ")

        # Plotting the boxplot
        st.write(f"Boxplot of `{product_filter}` ")

        fig, ax = plt.subplots()

        sns.boxplot(data=result, x="species", y="petal_width", ax=ax)
        st.pyplot(fig)
        query = (
            """
                select petal_length,sepal_length from mytable where species = '"""
            + product_filter
            + """'
                """
        )

        query = (
            """
        select petal_length,sepal_length from mytable where species = '"""
            + product_filter
            + """'
        """
        )

        tworesult = conn.sql(query).df()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(tworesult, kde=True, bins=30, color="blue", label="x")
        st.title("Histplot")

        st.pyplot(fig)


except (
    duckdb.CatalogException
):  # Catch exception when the database file don't exist yet
    st.text("Please Clik on the above button to generate data.")
