import streamlit as st
import pybase64
from st_clickable_images import clickable_images
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

def TeacherService(uname):
    task = st.selectbox("Menu", ["Schedule", "Duty", "Attendance"])
    if task == "Schedule":
        tab1, tab2 = st.tabs(["Individual Schedule", "Full Schedule"])

        with open(uname+".pdf", "rb") as f:
            base64_pdf = pybase64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf">'
        tab1.markdown(pdf_display, unsafe_allow_html=True)

        with open("schedule.pdf", "rb") as f:
            base64_pdf = pybase64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf">'
        tab2.markdown(pdf_display, unsafe_allow_html=True)

    elif task == "Duty":
        st.write("Duty table for this week ")
        with open("duty.pdf", "rb") as f:
            base64_pdf = pybase64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)

    elif task == "Attendance":
        c1, c2 = st.columns(2)
        cl = c1.selectbox("Select the class:", ["9A", "9G1", "9G2"])
        pr = c2.selectbox("Select the period:", ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th'])
        class_table = pd.read_csv(cl+".csv")
        tb = class_table[["SNo", "StudentName", pr]]
        ind=0
        for ind in tb.index:
            if pd.isna(tb[pr][ind]):
                tb[pr][ind] = "P"
        tb[pr][ind] = uname
        builder = GridOptionsBuilder.from_dataframe(tb)
        builder.configure_column(pr, editable=True)
        go = builder.build()
        agd = AgGrid(tb, gridOptions=go)
        if st.button("submit"):
            grid_table = agd['data']
            class_table[pr] = grid_table[pr].copy()
            class_table.to_csv(cl+".csv", index=False)
            st.success("Updated successfully")

def AdminService():
    task = st.selectbox("Menu", ["Schedule", "Duty", "Attendance", "Announcements", "Reset Password"])
    if task == "Schedule":
        t1, t2 = st.tabs(["Individual Schedule", "Full Schedule"])

        table = pd.read_excel("TeacherList.xlsx", sheet_name="Sheet1")
        teacher_list = table['TeacherID'].values.tolist()
        username = t1.selectbox("Select Your ID", teacher_list)
        uploaded_file = t1.file_uploader('Upload individual schedule here ', type="pdf")
        if uploaded_file is not None:
            with open(username+".pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            t1.success("File uploaded successfully")

        uploaded_file = t2.file_uploader('Upload full schedule here', type="pdf")
        if uploaded_file is not None:
            with open("schedule.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            t2.success("File uploaded successfully")


    elif task == "Duty":
        st.write("Please upload the duty for teachers")
        uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
        if uploaded_file is not None:
            with open("duty.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded successfully")

    elif task == "Attendance":
        st.write("You can download the attendance here")
        cl = ["9A", "9G1", "9G2"]
        pr = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th']
        c1 , c2 = st.columns(2)
        with pd.ExcelWriter('output.xlsx') as writer:
            for i in cl:
                pd_class = pd.read_csv(i+".csv")
                pd_class.to_excel(writer, sheet_name=i, index=False)
        with open("output.xlsx", "rb") as f:
            c1.download_button(
                label="Download Attendance",
                data=f,
                file_name='Att.xlsx',
                mime='text/xlsx')
        if c2.button("Reset"):
            for i in cl:
                pd_class = pd.read_csv(i+".csv")
                for j in pr:
                    pd_class[j] = pd.to_numeric(pd_class[j], errors='coerce')
                    pd_class.to_csv(i+".csv", index=False)
            c2.success("Reset successfully")

    elif task == "Announcements":
        tb = pd.read_excel("announcement.xlsx", sheet_name="Sheet1")
        if st.button("Show all announcements"):
            st.table(tb["Announcements"])
        c1, c2 = st.columns(2)
        ann = c1.text_input("Enter the new announcement here:")
        if c1.button("Submit"):
            if ann == "":
                c1.warning("Announcement should noe be empty!")
            else:
                tb1 = pd.DataFrame({'Announcements': [ann]})
                tb = tb.append(tb1, ignore_index=True)
                tb.to_excel("announcement.xlsx", sheet_name="Sheet1", index=False)
                c1.success("Announcement added successfully")

        dt = c2.text_input("Enter the number to delete the announcement:")
        if c2.button("Delete"):
            if dt == "":
                c2.warning("Number should not be empty")
            elif not dt.isdigit():
                c2.warning("enter number only")
            else:
                tb= tb.drop(tb.index[int(dt)])
                tb.to_excel("announcement.xlsx", sheet_name="Sheet1", index=False)
                c2.success("Announcement deleted successfully")

    elif task == "Reset Password":
        table = pd.read_excel("TeacherList.xlsx", sheet_name="Sheet1")
        teacher_list = table['TeacherID'].values.tolist()
        username = st.selectbox("Select teacher's ID", teacher_list)
        if st.button("Reset"):
            for ind in table.index:
                    if table['TeacherID'][ind] == username:
                        if not pd.isna(table['Password'][ind]):
                            table['Password'][ind] = pd.to_numeric(table['Password'][ind], errors='coerce')
                            table.to_excel("TeacherList.xlsx", sheet_name="Sheet1", index=False)
                            st.success("Password has been reset successfully")
                            break
                        else:
                            st.warning("Please ask teacher to sign up!")

st.markdown(
         f"""
         <style>
         .stApp {{
             background-image:url("https://img.freepik.com/free-vector/hand-drawn-colorful-science-education-wallpaper_23-2148489183.jpg?w=2000");
             background-repeat: no-repeat; 
             background-size:1400px 900px
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

st.header("Welcome to Hind Bint Maktoum School")
choice= st.sidebar.selectbox("Menu", ["Home", "Login", "Sign Up"])
if choice == "Home":
    col1, col2 = st.columns(2)
    col1.subheader("Home")
    col1.write("Term 2 Calendar – Academic Year 2022 – 2023")
    files = ["01-2022.PNG", "02-2022.PNG", "03-2022.PNG"]
    images = []
    for file in files:
        with open(file, "rb") as image:
            encoded = pybase64.b64encode(image.read()).decode()
            images.append(f"data:image/jpeg;base64,{encoded}")
    clicked = clickable_images(images,
                               titles=[f"Image #{str(i)}" for i in range(len(images))],
                               div_style={"display": "flex", "justify-content": "center", "flex-wrap": "nowrap"},
                               img_style={"margin": "5px", "height": "75px"})
    if clicked > -1:
        st.image(files[clicked])
    st.sidebar.subheader("Announcements")
    tb = pd.read_excel("announcement.xlsx", sheet_name="Sheet1")
    ann_list = tb["Announcements"].values.tolist()
    for ln in ann_list:
        st.sidebar.write(ln)
    
if choice == "Login":
    table = pd.read_excel("TeacherList.xlsx", sheet_name="Sheet1")
    teacher_list = table['TeacherID'].values.tolist()
    type = st.sidebar.selectbox("Type", ["Teacher", "Admin"])
    username = st.sidebar.selectbox("Select your ID", teacher_list)
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.checkbox("Login"):
        for ind in table.index:
            if table['TeacherID'][ind] == username and password == table['Password'][ind] and type == table['type'][ind]:
                st.sidebar.success("Login Successful")
                if type == "Teacher":
                    TeacherService(username)
                    break
                else:
                    AdminService()
                    break
        else:
            st.sidebar.warning("Password is wrong! Try again")

if choice == "Sign Up":
    st.subheader("Create a new account")
    table = pd.read_excel("TeacherList.xlsx", sheet_name="Sheet1")
    teacher_list = table['TeacherID'].values.tolist()
    pass_list = table['Password'].values.tolist()
    type = st.selectbox("Type", ["Teacher", "Admin"])
    username = st.selectbox("Select Your ID", teacher_list)
    password = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        if password == "":
            st.warning("Password should not be empty!")
        elif password.isdigit():
            st.warning("Password should not be only numbers")
        elif len(password) < 6:
            st.warning("Password should be more than 5 letters")
        else:
            table = pd.read_excel("TeacherList.xlsx", sheet_name="Sheet1")
            for ind in table.index:
                if table['TeacherID'][ind] == username:
                    if pd.isna(table['Password'][ind]):
                        table['Password'][ind] = password
                        table['type'][ind] = type
                        table.to_excel("TeacherList.xlsx", sheet_name="Sheet1", index=False)
                        st.success("Account created successfully")
                        break
                    else:
                        st.warning("You have signed up already. If you forget your password contact admin. ")

