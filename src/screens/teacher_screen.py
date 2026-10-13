import streamlit as st
from datetime import date
from src.ui.base_lyout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard

from src.components.subject_card import subject_card
from src.components.dialog_share_subject_code import share_subject_dialog
from src.database.db import check_teacher_exists,create_teacher,teacher_login,get_teacher_subjects,get_attendnce_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog


from src.pipelines.face_pipeline import predict_attendance

import numpy as np
from datetime import datetime
import pandas as pd

from src.database.config import supabase

def teacher_screen():

    style_background_dashboard()   # for color background
    style_base_layout()   # all project style and color layout
    

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type=="register":
        teacher_screen_register()
    
def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()    #is me teacher page ke sare header related ingormation
    with c2:
        st.markdown(
                f"""
                <h3 style="color: black; text-align: center;">
                    Welcome, {teacher_data.get('name', 'Teacher')}!
                </h3>
                """,unsafe_allow_html=True)
        if st.button("Logout",type='secondary',key='teacherloginbut',use_container_width=True):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',width='stretch',type=type1,icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_Subjects' else "tertiary"
        if st.button('Manage Subjects',width='stretch',type=type2,icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_Subjects'
            st.rerun()


    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',width='stretch',type=type3, icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_Subjects":
        teacher_tab_manage_Subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()




    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.markdown(f""" <h2 style = "color:black; font-size:20px; font-weight:400"> Take AI Attendance </h2> """,unsafe_allow_html=True)

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subject yet! Please create one to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}":s['subject_id'] for s in subjects}

    col1,col2 = st.columns([3,1],vertical_alignment="bottom",)

    with col1:
        selected_subject_label = st.selectbox('Select Subject ', options=list(subject_options.keys()))

    with col2:
        st.markdown("""
        <style>
        /* Select Subject label */
            div[data-testid="stSelectbox"] label p {
                color: green !important;
                font-size: 15px !important;
                font-weight: 600 !important;
            }

        /* Dropdown ke andar selected subject */
        div[data-testid="stSelectbox"] [data-baseweb="select"] {
            font-size: 10px !important;
            min-height: 25px !important;
        }
        </style>""", unsafe_allow_html=True)
        if st.button('Add Photos', type='primary',icon=':material/photo_prints:',width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()


    if st.session_state.attendance_images:
        st.markdown(f""" <h2 style="color:black;"> Added Photo </h2> """,unsafe_allow_html=True)
        gallery_cols = st.columns(4)

        for idx,img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.markdown("""
                <style>
                [data-testid="stImageCaption"] {
                    color: #06032e !important;
                    font-weight: 800 !important;}

                [data-testid="stImageCaption"] * {
                    font-weight: 800 !important;}
                </style>""", unsafe_allow_html=True)                
                st.image(img,width='stretch',caption=f'Image {idx+1}')
                
    has_photos = bool(st.session_state.attendance_images)
    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos',width='stretch',type='tertiary',icon=':material/delete:',disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        
        if st.button('Run Face Analysis',width='stretch',type='secondary',icon=':material/analytics:',disabled=not has_photos):
            with st.spinner('Deep Learning Classroom Photos...'):
                all_detected_ids = {}

            for idx,img in enumerate(st.session_state.attendance_images):
                img_np = np.array(img.convert('RGB'))
                detected,_,_ = predict_attendance(img_np)


                if detected:
                    for sid in detected.keys():
                        student_id = int(sid)

                        all_detected_ids.setdefault(student_id,[]).append(f"photo{idx+1}")


            enrolled_res = supabase.table('subject_student').select("*,students(*)").eq('subject_id',selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No student enrolled in this course')

            else:
                results,attendance_to_log = [],[]
                current_timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")


                for node in enrolled_students:
                    student = node['students']
                    sources = all_detected_ids.get(int(student['student_id']),[])
                    is_present = len(sources) > 0

                    results.append({
                        "Name":student['name'],
                        "ID":student['student_id'],
                        "source":",".join(sources) if is_present else "_",
                        "status": "✅ present" if is_present else "❌ Absent"
                    })

                    attendance_to_log.append({
                        'student_id':student['student_id'],
                        'subject_id':selected_subject_id,
                        'timestamp':current_timestamp,
                        'is_present':bool(is_present)
                    })

                attendance_result_dialog(pd.DataFrame(results),attendance_to_log)

    with c3:
        if st.button('Use Voice Attendnce',type='primary',width='stretch',icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)






            

            





def teacher_tab_manage_Subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f""" <h2 style="color:#3b3a45;font-weight: 400;
            letter-spacing:2px;word-spacing: 10px;"> Manage Attendance </h2> """,
            unsafe_allow_html=True )
    with col2:
        st.markdown("""
        <style>
            div.st-key-create_subject_btn {
                transform: translateX(10px);
            }
        </style>""", unsafe_allow_html=True)
        if st.button('Create New Subjects', width='stretch',key="create_subject_btn"):
            create_subject_dialog(teacher_id)

    #  list alll subject 
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👨🏽‍🎓","students",sub['total_students']),
                ("👩🏽‍🏫","classes",sub['total_classes'])

            ]

        def share_btn():
            if st.button(f"share code: {sub['name']}",key=f"share_{sub['subject_code']}",icon=":material/share:"):
                share_subject_dialog(sub['name'],sub['subject_code'])
            st.space() 

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats = stats,
            footer_callback = share_btn

            )
    else:
        st.info("No SUBJECTS FOUND. CREATE ONE ABOVE")



def teacher_tab_attendance_records():
    st.markdown(f""" <h2 style = "color:black; font-weight:300"> Attendance Records </h2>
    """,unsafe_allow_html=True)

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendnce_for_teacher(teacher_id)

    if not records:
        return
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group":ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%m %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present',False))
        })

    df = pd.DataFrame(data)


    summary = (
        df.groupby(['ts_group','Time','Subject','Subject Code'])
        .agg(
            present_count = ('is_present','sum'),
            Total_Count = ('is_present','count')
        ).reset_index()
    )

    summary['Attendance Stats'] = (
        "✅" + summary['present_count'].astype(str) + " /"
        + summary['Total_Count'].astype(str) + 'Students'
    )

    display_df = (summary.sort_values(by='ts_group',ascending=False)
    [['Time','Subject','Subject Code','Attendance Stats']]
    )

    st.dataframe(display_df, width='stretch', hide_index=True)


    

def login_teacher(username,password):
    if not username or not password:
        return False

    teacher = teacher_login(username,password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

def teacher_screen_login():
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
            Login using password </h2>  """, unsafe_allow_html=True)

    st.space()
   
    st.markdown("""
        <style>

            [data-testid="stTextInput"] label p {
                color: black !important;
            }

            [data-testid="stTextInput"] input {
                color: white !important;
                background-color: #262632 !important;
            }

            [data-testid="stTextInput"] input::placeholder {
                color: white !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInput"] input:focus::placeholder {
                opacity: 0 !important;
            }
          
        </style>
        """, unsafe_allow_html=True)

    teacher_username = st.text_input("Enter Username",placeholder='viveksahu@123',key='teacher_login_username')  

    teacher_pass = st.text_input("Enter Password",placeholder='Enter your password',type='password',key='teacher_login_password')  

    st.divider()

    btncl, btnc2 = st.columns(2)

    with btncl:
        if st.button('Login',icon=':material/passkey:',width='stretch'):
            if not teacher_username or not teacher_pass:
                st.warning("Please enter username and password")
            elif login_teacher(teacher_username,teacher_pass):
                st.toast("Welcome back!",icon="👍")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("InValid username & password ")
        

    with btnc2:
        if st.button('Register Instead',type='primary', icon=':material/app_registration:',width='stretch'):
            st.session_state.teacher_login_type='register'

    footer_dashboard()


def register_teacher(teacher_username,teacher_name,teacher_pass,teacher_pass_confirm):
    teacher_username = teacher_username.strip()
    teacher_name = teacher_name.strip()
    teacher_pass = teacher_pass.strip()
    teacher_pass_confirm = teacher_pass_confirm.strip()
    
    if not teacher_username or not teacher_name or not teacher_pass or not teacher_pass_confirm:
        return False,"All fields are requird !"
    if check_teacher_exists(teacher_username):
        return False,"username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False,"password doesn't match"

    try:
        create_teacher(teacher_username,teacher_pass,teacher_name)
        return True,"Successfully Created! Login Now"
    except Exception as e:
        return False,f"unexpected Error!{e}"

def teacher_screen_register():
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()    #is me teacher page ke sare header related ingormation
    with c2:
        if st.button("Go back to home",type='secondary',key='teacherregisterbut',shortcut="Control+Backspace"):
            st.session_state['login_type'] = None
            st.rerun()
    
    st.space()
        
    st.markdown("""
            <h2 style="color: black; text-align:center; font-weight: 300; font-size: 40px;">
                Register your self </h2>  """, unsafe_allow_html=True)
    
    st.space()
       
    st.markdown("""
        <style>
    
            [data-testid="stTextInput"] label p {
                color: black !important;
            }
    
            [data-testid="stTextInput"] input {
                color: white !important;
                background-color: #262632 !important;
            }
    
            [data-testid="stTextInput"] input::placeholder {
                color: white !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInput"] input:focus::placeholder {
                opacity: 0 !important;
            }
              
            </style>
            """, unsafe_allow_html=True)
    
    teacher_username = st.text_input("Enter Username",placeholder='viveksahu@123',key='teacher_register_username')

    teacher_name = st.text_input("Enter Name",placeholder='vivek sahu',key='teacher_register_name')  

    # teacher_DOB = st.date_input("Enter your DOB",max_value=date.today(),format="DD/MM/YYYY")
    
    teacher_pass = st.text_input("Enter Password",placeholder='Enter password',type='password',key='teacher_register_password')  

    teacher_pass_confirm = st.text_input("Confirm your Password",placeholder='Confirm password',type='password',key='teacher_register_confirm_pass')  

    st.divider()

    btncl, btnc2 = st.columns(2)
    
    with btncl:
        if st.button('Register now',icon=':material/passkey:',width='stretch'):
            success,message = register_teacher(teacher_username,teacher_name,teacher_pass,teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(3)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
    
    with btnc2:
        if st.button('Login Instead',type='primary', icon=':material/app_registration:',width='stretch'):
            st.session_state.teacher_login_type = 'login'
    
    footer_dashboard()
        
    