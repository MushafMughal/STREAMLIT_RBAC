import streamlit as st
import pandas as pd
import pymysql
st.set_page_config(layout="wide")

def db():
        return pymysql.connect(
            host='192.168.18.206',  # Remote MySQL Server IP
            user='root',
            password='mydb1234@XTI#2025',
            database='my_db',
            port=3306
        )
   
mydb = db()
cursor = mydb.cursor()

def get_data(Market,training):
    df = pd.read_excel("Calling Tree - Feb-25 V3.xlsx")
    Market = Market.upper()
    if training:
        df["Store Type"] = df["Store Type"].str.strip()
        df = df[df["Store Type"].isin(["Training Store", "Outskirt Training Store"])]
        df = df[df["Market"] == Market]
    else:
        df = df[df["Market"] == Market]
    
    res = df["Store"].tolist()  
    return res

def get_market():
    df = pd.read_excel("Calling Tree - Feb-25 V3.xlsx")

    res = df["Market"].unique().tolist()
    return res

css = """
<style>
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div > div > div > div:nth-child(6) > div:nth-child(2) > div > div > div > div > div > div {
        BACKGROUND-COLOR: #f0f2f6;
        border-radius: 0.5rem;
        padding-left: 1rem;
    }
 
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# CSV file name
CSV_FILE = "employee_data.csv"

st.markdown("<h1 style='text-align: center;'>NTID Form</h1>", unsafe_allow_html=True)

# Form inputs
with st.container(border=True):
    cola, colb = st.columns(2)
    with cola:
        your_name = st.text_input("Your Full Name (Person filling out this form)")
    with colb:
        employee_name = st.text_input("Employee's Full Name")
        
        
    cola, colb = st.columns(2)
    with cola:
        date = st.date_input("Date")
    with colb:
        language = st.multiselect("Select Language", ["English", "Spanish"])
        if isinstance(language, list):
            language = ", ".join(language)

    cola, colb = st.columns(2)
    with cola:
        pay_type = st.selectbox("Select Pay Type", ["Hourly", "Salary"])
    with colb:
        pay_rate = st.text_input("Pay Rate (e.g. 12 for hour or 1200 for salary)")

    cola, colb = st.columns(2)
    with cola:
        email = st.text_input("Email Address")
    with colb:
        phone = st.text_input("Phone Number")


    cola, colb = st.columns(2)
    with cola:
        size_options = [
        "Not Required","Male XS", "Male S", "Male M", "Male L", "Male XL", "Male 2XL", "Male 3XL", "Male 4XL",
        "Female XS", "Female S", "Female M", "Female L", "Female XL", "Female 2XL", "Female 3XL", "Female 4XL"
        ]
        # Streamlit selectbox
        t_shirt_size = st.selectbox("Select T-Shirt Size:", size_options, placeholder="Choose an option")

    with colb:
        badge_name = st.text_input("Provide Name for the Badge")

    cola, colb = st.columns(2)
    with cola:
        position = st.selectbox("Sub Dealer Retails Sales Representative", ["Sub Dealer Retails Sales Representative", "Sub Dealer Store Manager","Dealer Retail Sales Representative","Dealer Store Manager"])
    with colb:       
        training_completed = st.radio("Has the employee completed their training?", ["Yes", "No", "Other"],horizontal=True, index=2)

    # Conditional inputs
    training_details = None
    proof_of_training = None
    market_selection = None
    training_proof = None
    file_type = None

    if training_completed == "Other":
        training_details = st.text_area("Please provide details")
        Primary_Door = None
        Secondary_Door = None

    elif training_completed == "Yes":
        proof_of_training = st.file_uploader("Please provide proof of the training completion",type=["png", "jpg", "jpeg", "pdf"])
        if proof_of_training:
            training_proof = proof_of_training.read()  # Read file as binary
            file_type = proof_of_training.type  # Get MIME type

    if training_completed == "Yes" or training_completed == "No":
        market_selection = st.selectbox("Select Market", get_market())      
        
        cola, colb = st.columns(2)
        with cola:
            data =get_data(market_selection,True)
            Primary_Door = st.multiselect("Select Primary Door", data)
            if isinstance(Primary_Door, list):
                Primary_Door = ", ".join(Primary_Door)
                
        with colb:
            data =get_data(market_selection,False)
            Secondary_Door = st.multiselect("Select Secondary Door", data)
            if isinstance(Secondary_Door, list):
                Secondary_Door = ", ".join(Secondary_Door)

# Submit button
if st.button("Submit"):
    if training_completed != "Other":
        if len(Primary_Door) == 0 or Primary_Door == None:
            st.warning("Please select Primary Door")
            st.stop()
        elif Secondary_Door == None or len(Secondary_Door) == 0:
            st.warning("Please select Secondary Door")
            st.stop()

    if training_completed == "Other" and (training_details == "" or training_details == None):
        st.warning("Please provide training details")
        st.stop()
    
    if training_completed == "Yes" and proof_of_training == None:
        st.warning("Please provide proof of training completion")
        st.stop()

    # Insert data into MySQL
    sql = """
        INSERT INTO NTID_REQUEST_DETAILS (
            fillers_email, your_name, employee_name, date, pay_rate, pay_type, 
            position, email, phone, t_shirt_size, badge_name, language, 
            training_completed, training_details, market_selection,primary_door,secondary_door,
            training_proof, file_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        email, your_name, employee_name, date, pay_rate, pay_type,
        position, email, phone, t_shirt_size, badge_name, language,
        training_completed, training_details, market_selection,Primary_Door,Secondary_Door,training_proof, file_type
    )

    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()
    mydb.close()

    st.success("Form Submitted Successfully! Data saved to Database.")


# Display stored data (Optional)
mydb = db()
df = pd.read_sql("SELECT * FROM NTID_REQUEST_DETAILS", mydb)
mydb.close()

st.dataframe(df)  # Show table data in Streamlit