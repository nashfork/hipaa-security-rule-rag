import streamlit as st
from src.retrieve import retrieve_chunks
from src.generate import generate_response

# Page config
st.set_page_config(
    page_title='HIPAA Security Rule Assistant',
    page_icon='🏥',
    layout='centered'
)

# Header
st.title('HIPAA Security Rule Changes Assistant')
st.markdown(
    'Ask plain-English questions about the proposed 2025 HIPAA Security Rule changes '
    'and receive cited answers drawn directly from the regulatory text'
)
st.divider()

# Example queries as clickable buttons
st.markdown('**Example queries:**')
example_queries = [
    "What are the proposed changes to multi-factor authentication requirements?",
    "Does the NPRM introduce new requirements for incident response planning?",
    "What does the proposed rule say about encryption of data at rest?"
]

if 'query' not in st.session_state:
    st.session_state.query=''

cols=st.columns(len(example_queries))
for i, (col, example) in enumerate(zip(cols, example_queries)):
    if col.button(example, key=f'example_{i}', use_container_width=True):
        st.session_state.query = example

# Query input
query = st.text_area(
    'Your question:',
    value=st.session_state.query,
    height=100,
    placeholder='Enter your question about the proposed HIPAA Secuirty Rule changes...'
)

# Submit
if st.button('Submit', type='primary'):
    if query.strip():
        with st.spinner('Retrieving relevant context and generating response...'):
            results = retrieve_chunks(query)
            answer = generate_response(query, results)
        st.divider()
        st.markdown(answer)
    else:
        st.warning('Please enter a question before submitting.')

# Footer
st.divider()
st.caption(
    'This tool is for research and informational purposes only and is not a substitute '
    'for legal or compliance advice. Not approved for use with real PHI.'
)
