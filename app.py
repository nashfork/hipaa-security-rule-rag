import gradio as gr
from src.retrieve import retrieve_chunks
from src.generate import generate_response

def query_rag(query):
    if not query.strip():
        return "Please enter a question before submitting."
    results = retrieve_chunks(query)
    answer = generate_response(query, results)
    return answer

example_queries = [
    ["What are the proposed changes to multi-factor authentication requirements?"],
    ["Does the NPRM introduce new requirements for incident response planning?"],
    ["What does the proposed rule say about encryption of data at rest?"]
]

with gr.Blocks(title="HIPAA Security Rule Changes Assistant") as demo:
    gr.Markdown("# HIPAA Security Rule Changes Assistant")
    gr.Markdown(
        "Ask plain-English questions about the proposed 2025 HIPAA Security Rule changes "
        "and receive cited answers drawn directly from the regulatory text."
    )

    query_input = gr.Textbox(
        label="Your question:",
        placeholder="Enter your question about the proposed HIPAA Security Rule changes...",
        lines=3
    )

    gr.Examples(
        examples=example_queries,
        inputs=query_input,
        label="Example queries"
    )

    submit_btn = gr.Button("Submit", variant="primary")
    output = gr.Markdown(label="Response")

    submit_btn.click(
        fn=query_rag,
        inputs=query_input,
        outputs=output
    )

    gr.Markdown(
        "---\n*This tool is for research and informational purposes only and is not a "
        "substitute for legal or compliance advice. Not approved for use with real PHI.*"
    )

if __name__ == "__main__":
    demo.launch()