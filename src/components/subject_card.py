import streamlit as st



def subject_card(name,code,section,stats=None,footer_callback=None):
    html = f"""
        <div style ="background:white; border-left:8px solid #EB459E; padding:25px; border-radius:20px; border:1px solid black; margin-bottom:20px;">
            <h3 style="margin:0; color:#1e293b; font-size:1.5rem;">{name}</h3>
        <p style="color:#64748b; margin:10px 0;">code : <span style="background:#E0E3FF; color:#5868F2; padding:2px 8px border-radius:5px;">{code}</span> | section : {section} </p>
        """
    if stats:
        html += """
            
            """

    for icon, label, value in stats:
        html += f"""
        <div style="
            background:#FFF1F6;
            color:#334155;
            padding:10px 18px;
            border-radius:25px;
            font-size:18px;
            font-weight:600;
            display:inline-flex;
            align-items:center;
            gap:5px;
        ">
            <span>{icon}</span>
            <span>{value} {label}</span>
        </div>
        """

    html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()


































