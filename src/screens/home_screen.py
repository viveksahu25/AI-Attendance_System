import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_lyout import style_base_layout,style_background_dashboard,style_background_home



def home_screen():
    # st.header('home_screen')

    header_home()
    style_base_layout()
    style_background_dashboard()
    style_background_home()

    col1, col2 = st.columns(2,gap="large")

    with col1:
        st.markdown(
            '<h2 style="color:black; margin:0 0 5px 0; font-weight:300;">I\'m Teacher</h2>',
            unsafe_allow_html=True)
        st.image("aasist/teachers_img.png", width=120)
        if st.button("Teacher Login",type="primary",icon=":material/arrow_outward:",icon_position="right"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    with col2:
        st.markdown(
            '<h2 style="color:black; margin:0 0 5px 0;font-weight:300">I\'m Student</h2>',
                    unsafe_allow_html=True)
        st.image("aasist/students_img.png", width=120)
        if st.button("Student Login",type="primary",icon=":material/arrow_outward:",icon_position="right"):
            st.session_state['login_type'] = 'student'
            st.rerun()

    footer_home()