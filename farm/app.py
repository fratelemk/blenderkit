import streamlit as st
import subprocess


st.title("BlendKit")

version = subprocess.run(["blender", "--version"], check=True, capture_output=True)
head = subprocess.run(["head", "-1"], input=version.stdout, capture_output=True)
st.info(head.stdout.decode().strip())

if st.button("Create demo scene"):
    ps = subprocess.run(["blender", "-b", "--python", "scripts/create_demo_scene.py"])


uploaded_file = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)

    st.button("Transfer to nodes")
