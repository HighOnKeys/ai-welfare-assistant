import streamlit as st

from backend.eligibility import get_eligible_schemes

from backend.rag import get_scheme_info


st.set_page_config(
    page_title="AI Welfare Assistant",
    page_icon="🇮🇳",
    layout="wide"
)

st.title(
    "🇮🇳 AI Welfare Scheme Assistant"
)

st.info(
    """
    This assistant helps users discover welfare schemes
    they may qualify for using AI-powered recommendations.
    """
)

st.write(
    "Discover government schemes you may qualify for."
)

language = st.selectbox(
    "Select Language",
    ["English", "Hindi"]
)

gender = st.selectbox(
    "Gender",
    ["Male", "Female"]
)

occupation = st.selectbox(
    "Occupation",
    ["Farmer", "Unorganised Worker", "Other"]
)

income = st.number_input(
    "Annual Family Income (₹)",
    min_value=0,
)

house = st.selectbox(
    "Do you own a pucca house?",
    ["Yes", "No"]
)

rural = st.selectbox(
    "Do you live in a rural area?",
    ["Yes", "No"]
)

girl_child = st.selectbox(
    "Do you have a girl child below 10 years?",
    ["Yes", "No"]
)

age = st.number_input(
    "Your Age",
    min_value=0,
    max_value=100
)

bpl_card = st.selectbox(
    "Do you have a BPL / priority household ration card?",
    ["Yes", "No"]
)

if st.button("Find Eligible Schemes"):
    user = {
        "occupation": occupation,
        "income": income,
        "house": house,
        "gender": gender,
        "rural": rural,
        "girl_child": girl_child,
        "age": age,
        "bpl_card": bpl_card,
    }

    schemes, notes = get_eligible_schemes(user)

    st.success(
        f"Found {len(schemes)} schemes."
    )

    for scheme in schemes:
        st.subheader(scheme)
        query = f"""

Explain the scheme:

{scheme}

Mention:

1. Benefits

2. Eligibility

3. Required Documents

4. Application Process

"""
        if language == "Hindi":

            query += (
                "\nAnswer in Hindi."
            )
        response = get_scheme_info(
            query
        )

        with st.expander(
            f"View details for {scheme}"
        ):
            st.markdown(response)

            st.download_button(
                "Download Checklist",
                response,
                file_name=f"{scheme}.txt"
            )
st.divider()

st.subheader("Ask about any welfare scheme")

user_question = st.text_input(
    "Enter your question"
)

if st.button("Ask"):

    response = get_scheme_info(
        user_question
    )

    st.write(response)
