import streamlit as st
import base64
from pathlib import Path


def header_home():
    # Local image ka path
    logo_path = (
        Path(__file__).resolve().parents[2]
        / "aasist"
        / "snap_class_logo.png"
    )

    # Image ko Base64 me convert karna
    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    # Is block ko indent karke function ke andar rakhna hai
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:20px; margin-top:30px;">
            <img src="data:image/png;base64,{logo_base64}" style="height:100px;">
            <h1 style="text-align:center; color:red !important; margin-top:10px;">
                SNAP<br>CLASS
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )


# import streamlit as st

def header_dashboard():
    # Local image ka path
        logo_path = (
            Path(__file__).resolve().parents[2]
            / "aasist"
            / "snap_class_logo.png"
        )
    
        # Image ko Base64 me convert karna
        logo_base64 = base64.b64encode(
            logo_path.read_bytes()
        ).decode("utf-8")
    
        # Is block ko indent karke function ke andar rakhna hai
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:center; gap:10px; ">
                <img src="data:image/png;base64,{logo_base64}" style="height:100px;">
                <h2 style="text-align:left; color:#2d2fb3; font-weight:400; margin-top:10px;">
                    SNAP<br>CLASS
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
     