### import packages that will be necessary down the line
import time

import duckdb
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st


## connecting to duckdb
conn = duckdb.connect()

# making a query that creates the table from my dataset downloaded from the internet
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
# Creates table (executes the query above)
conn.execute(query)

# Part 1: Testing with Duck DB show()
start_time = time.time()

## select all the datatable (* means all columns)
query = """
select * 
from mytable
"""
# transform into dataframe (same as R)
df = conn.sql(query).df()


# title of the dashboard
st.title("Streamlit + duckdb Tutorial")
try:
    #create a button to use
    button = st.button(label="Check for a sample")

    # if button is pressed do something
    if button:
        # title if button is pressed
        st.write("## Sample")
        # show dataframe (first 10 rows) if button is pressed.
        st.dataframe(df.head(10), height=300)

    # another title
    st.write("## Visualization")
    ## create a selection box with the 4 options (sepal and petal length and width)
    option = st.selectbox(
        "Select a dimension",
        ["sepal_length", "sepal_width", "petal_width", "petal_length"],
        key="option",
    )
    # if a option is selected show something
    if option:
        # second option to use in double plots
        option2 = st.selectbox(
            "Select another dimension",
            ["sepal_length", "sepal_width", "petal_width", "petal_length"],
            key="option2",
        )
        # another title (is using markdown - hence the ###)
        st.write(f"### Scatter Plot: {option} x {option2}")

        ## create a scatter plot 
        fig = px.scatter(
            df,
            x=option,
            y=option2,
            color="species",
            hover_name="species",
            log_x=True,
        )

        # This is the default. So you can also omit the theme argument.
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
        # another title
        st.write(f"### Boxplot: {option} x Specices")
        # another setup of plot
        fig, ax = plt.subplots()


        # a boxplot with the seaborn lib (see above)
        sns.boxplot(data=df, x="species", y=option, ax=ax)
        # adding it to the dashboard
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
