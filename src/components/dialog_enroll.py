import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog("Enroll in Subjects")
def enroll_dialog():
    st.write('Enter the subject code provided by your teacher to enroll')

    join_code = st.text_input(
    'subject_code',
    value=st.query_params.get("join-code", ""),
    placeholder='Eg. CS-201'
        )

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code.strip():

            res = supabase.table('subjects').select(
                'subject_id, name, subject_code'
            ).eq('subject_code', join_code.strip()).execute()

            if res.data:
                subject = res.data[0]

                student_data = st.session_state.get('student_data')

                if not student_data:
                    st.error('Student data not found!')
                    return

                student_id = student_data['student_id']

                check = supabase.table('subject_student').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()

                if check.data:
                    st.warning('You are already enrolled in this subject')

                else:
                    enroll_student_to_subject(
                        student_id,
                        subject['subject_id']
                    )
                    st.success('Successfully enrolled')
                    st.toast(f"Enrolled {subject['name']} Successfully!")
                    time.sleep(1)
                    st.rerun()

            else:
                st.error('Invalid subject code!')

        else:
            st.warning('Please enter a subject code')