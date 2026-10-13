
import streamlit as st
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():

    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon='aasist/snap_class_logo.png'
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    join_code = st.query_params.get('join-code')

    if join_code and st.session_state['login_type'] != 'student':
        st.session_state['login_type'] = 'student'
        st.rerun()

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()

    if join_code:
        student_data = st.session_state.get('student_data')

        if (
            st.session_state.get('login_type') == 'student'
            and isinstance(student_data, dict)
            and student_data.get('student_id') is not None
        ):
            auto_enroll_dialog(join_code)


if __name__ == '__main__':
    main()