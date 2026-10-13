import streamlit as st
from PIL import Image
import  numpy as np
import time

from src.ui.base_lyout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance,get_face_embeddings,train_classifier
from src.pipelines.voice_pipline import get_voice_embedding
from src.database.db import get_all_students,create_student,get_student_subject,get_student_attendance,unenroll_student_to_subject
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card



def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()    #is me teacher page ke sare header related ingormation
    with c2:
        st.markdown(
            f"""
            <h3 style="color: black; text-align: center;">
                Welcome, {student_data.get('name', 'Teacher')}!
            </h3>""",unsafe_allow_html=True)
        if st.button("Logout", type="secondary", key="student_logout", use_container_width=True):

            st.session_state["is_logged_in"] = False
            st.session_state.pop("student_data", None)
            st.session_state.pop("user_role", None)
            st.session_state["login_type"] = None

            st.rerun()

    st.space()

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f""" <h2 style="color:black;font-size: 20px; font-weight: 400;">your enrolled subjects </h2> 
           """,unsafe_allow_html=True)
    with c2:
        if st.button('Enroll in subjects',type='primary',width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('loading your enrolled subject...'):
        subjects = get_student_subject(student_id)
        logs = get_student_attendance(student_id)


    stats_map = {}

    for log in logs:
        sid = log['student_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0,"attended":0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0,"attended":0})
        def unenroll_button(subject_id=sid):
            if st.button("Unenroll from this course",type='tertiary',width='stretch',key=f"unenroll_{subject_id}",icon=':material/delete_forever:'):
                # try:
                    result = unenroll_student_to_subject(
                        student_id,
                        subject_id
                    )

                    # st.write("Delete result:", result)

                    if result:
                        st.success("Successfully unenrolled!")
                        st.toast(f"Unenrolled from{sub['name']} Successfully!")
                        st.rerun()
                    else:
                        st.error("No row deleted. Check RLS or student/subject ID.")

                # except Exception as e:
                #     st.error(f"Database error: {e}")
                

        

        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats =[
                    ('📅','Total',stats['total']),
                    ('✅','Attended',stats['attended'])

                ],
                footer_callback=unenroll_button
                
            )
            
        

    footer_dashboard()

def student_screen():


    style_background_dashboard()   # for color background
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return




    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()    #is me teacher page ke sare header related ingormation
    with c2:
        if st.button("Go back to home",type='secondary',key='teacherloginbut',shortcut="Control+Backspace"):
            st.session_state['login_type'] = None
            st.rerun()
            
        st.space()
        
    st.markdown("""
            <h2 style="color: black; text-align:center; font-weight: 300; font-size: 40px;">
                Login using FaceID </h2>  """, unsafe_allow_html=True)
    
    st.space()
    st.space()

    st.markdown("""
        <style>
            [data-testid="stCameraInput"] label p {
             color: red !important;
            font-size: 22px !important;
            font-weight: 700 !important;
                }
        </style>
            """, unsafe_allow_html=True)

    show_registration = False

    
    photo_source = st.camera_input("Position your face in the center")
    

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is Scanning...'): 
            detected,all_ids,num_faces = predict_attendance(img)

            if num_faces ==0:
                st.warning('Face not found')
            elif num_faces >1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id']==student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"welcome back{student['name']}")
                        time.sleep(1)
                        st.rerun()


                else:
                    st.info('Face not recognized! you might be a new student !')
                    show_registration = True


    if show_registration:

       
        
        with st.container(border=True):
            st.markdown("""
                <h2 style="color: #042f30;font-size: 30px;font-weight: 400;margin-bottom: 15px;">
                    Register new profile
                </h2>""", unsafe_allow_html=True)
            st.markdown("""
                <style>
                    div[data-testid="stTextInput"] label p {
                        color: #5865F2 !important;}
                </style>""", unsafe_allow_html=True)
            new_name = st.text_input("Enter your name",placeholder='E.g. vivek sahu')

            st.markdown("""<h2 style="color: #042f30;font-size: 30px;font-weight: 400;margin-bottom: 15px;">
                    optional : Voice Enrollment </h2>""",unsafe_allow_html=True)
            st.info('Enroll your for voice only attendance')

            audio_data = None
            try:
                st.markdown("""
                    <style>
                        /* Audio input ka label color */
                        [data-testid="stAudioInput"] label p {
                            color: #5865F2 !important;
                            font-size: 15px !important;
                            font-weight: 400 !important;
                        }
                    </style>""", unsafe_allow_html=True)

                audio_data = st.audio_input('Record a short pharse like I am present My name is vivek sahu')
            except Exception:
                st.error('Audio data Failed !')


            if st.button('Create Account',type='primary'):
                if new_name:
                    with st.spinner('Creating Profile...'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb,voice_embedding = voice_emb)

                            if response_data:
                                train_classifier()

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile created ! Hi {new_name}')
                                time.sleep(1)
                                st.rerun()

                            else:
                                st.error('Couldnt capture your facial features for registration')



                else:
                    st.warning('please enter your name')

            
                
    footer_dashboard()
