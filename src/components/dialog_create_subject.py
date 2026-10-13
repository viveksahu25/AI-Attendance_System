import streamlit as st
from src.database.db import create_subject 


@st.dialog("create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the detail of New Subject")
    sub_id = st.text_input("Subject Code",placeholder="CS - 101")
    sub_name = st.text_input("Subject Name",placeholder="Introduction to computer")
    sub_section = st.text_input("Section",placeholder="A")


    if st.button("Create Subject now", type='primary',width='stretch'):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name,sub_name,teacher_id)
                st.toast("subject created Succesfully")
                st.rerun()

            except Exception as e:
                st.error(f"Error:{str(e)}")

        else:
            st.Warning("Please fill all the fields")