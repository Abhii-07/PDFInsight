import streamlit as st

# Define functions for each page
def home_page():
    st.title("Home Page")
    st.write("Welcome to the Home Page. This is where you can provide some information about your app.")

def about_page():
    st.title("About Page")
    st.write("Welcome to the About Page. Here, you can provide details about your app or team.")

def contact_page():
    st.title("Contact Page")
    st.write("Welcome to the Contact Page. You can add contact information or a contact form here.")

# Navbar navigation
st.title("Multi-Page App Navigation")

# Create a navbar to select pages
selected_page = st.radio("Navigate", ["Home", "About", "Contact"])

# Main function to render selected page
def main():
    if selected_page == "Home":
        home_page()
    elif selected_page == "About":
        about_page()
    elif selected_page == "Contact":
        contact_page()

if __name__ == "__main__":
    main()
