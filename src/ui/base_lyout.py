import streamlit as st



def style_background_home():


    st.markdown("""
        <style>

            .stApp{
            background:#5865F2 !important;
            }
            .stApp div[data-testid="stColumn"]{
            background-color:#E0E3FF !important;
            padding:2rem !important;
            border-radius:5rem !important;
            transform: translateY(-40px);
            }

        </style>


              """, unsafe_allow_html=True)


def style_background_dashboard():


    st.markdown("""
        <style>

            .stApp{
            background:#E0E3FF !important;
            }

        </style>


              """, unsafe_allow_html=True)



def style_base_layout():


    st.markdown("""

        <style>
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1986&family=Outfit:wght@100..900&display=swap');
        
        /* Streamlit ka header aur toolbar poori tarah hide karne ke liye */
            [data-testid="stHeader"] {
                display: none !important;
        }
        
        /* Footer ko hide karne ke liye */
            footer {
                display: none !important;
        }

            .block-container, 
            [data-testid="stMainBlockContainer"], 
            [data-testid="stAppViewBlockContainer"] {
                padding-top: 1.5rem !important;
            }

            h1{
                font-family:'climate crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0rem !important;
                
                

                }

            h2{
                font-family:'climate crisis', sans-serif !important;
                font-size: 1.8rem !important;
                line-height: 0.9 !important;
                margin-bottom: 0rem !important;

                
                
                
                
                }

            h3, h4, p {
                 font-family: 'outfit', sans-serif;
                 }

                button[kind="primary"]{
                background: #5865F2 !important;
                border-radius: 50px !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="secondary"] {
                background: #EB459E !important;
                
                border-radius: 1.5rem !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }  

            button[kind="tertiary"] {
                background: black !important;
                border-radius: 1.5rem !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }   

            button:hover{
                    transform:scale(1.03)
                    }   
        
        </style>


              """, unsafe_allow_html=True)