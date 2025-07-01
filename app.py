import streamlit as st
from rag_system import retrieve_and_answer, save_correction

st.title("🔍 RAG Q&A System")

question = st.text_input("Ask a question:")

if st.button("Get Answer"):
    result = retrieve_and_answer(question)
    st.session_state["result"] = result
    st.write("### Answer:")
    st.write(result)

if "result" in st.session_state:
    st.markdown("---")
    st.subheader("Was this answer correct?")
    col1, col2 = st.columns(2)

    if col1.button("Yes"):
        st.success("Thank you!")

    if col2.button("No"):
        corrected_answer = st.text_area("Edit the answer:", value=st.session_state["result"])
        #reviewer = st.text_input("Your name:")
        if st.button("Save Correction"):
            """if not reviewer:
                st.error("Please enter your name.")"""
            if not corrected_answer:
                st.error("Please provide a corrected answer.")
            else:
                save_correction(
                    question,
                    st.session_state["result"],
                    corrected_answer
                )
                st.success("✅ Correction saved!")