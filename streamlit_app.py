import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="ScholarScope - AI Research Copilot",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background: #000000; }
    h1 { color: #FFD700 !important; font-weight: 900 !important; font-size: 3.5rem !important; }
    .subtitle { font-size: 18px; color: #999; letter-spacing: 2px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

if 'pdf_chunks' not in st.session_state:
    st.session_state.pdf_chunks = None
if 'pdf_embeddings' not in st.session_state:
    st.session_state.pdf_embeddings = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.markdown('<h1>SCHOLARSCOPE</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered PDF Research Assistant</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### Upload Your Research Paper")

uploaded_file = st.file_uploader("Drop your PDF here", type="pdf")

if uploaded_file:
    if st.button("🔄 PROCESS PDF", type="primary"):
        with st.spinner("Processing..."):
            try:
                from ingestion.pdf_processor import get_pdf_processor
                
                processor = get_pdf_processor()
                chunks = processor.extract_text_from_pdf(uploaded_file)
                st.success(f"✅ Extracted {len(chunks)} chunks")
                
                embeddings, chunks = processor.create_embeddings(chunks)
                
                st.session_state.pdf_chunks = chunks
                st.session_state.pdf_embeddings = embeddings
                st.session_state.chat_history = []
                
                st.success("🎉 Ready to chat!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if st.session_state.pdf_chunks:
    st.markdown("---")
    st.markdown("### Chat with Your Paper")
    
    for chat in st.session_state.chat_history:
        st.markdown(f"**🙋 You:** {chat['question']}")
        st.markdown(f"**🤖 AI:** {chat['answer']}")
        st.markdown("---")
    
    with st.form(key='chat', clear_on_submit=True):
        question = st.text_input("Ask anything...", key="q")
        submit = st.form_submit_button("🤖 ASK AI", type="primary")
        
        if submit and question:
            try:
                from ingestion.pdf_processor import get_pdf_processor
                from ingestion.llm_handler import get_llm_handler
                
                processor = get_pdf_processor()
                llm = get_llm_handler()
                
                with st.spinner("Thinking..."):
                    chunks = processor.search_chunks(
                        question,
                        st.session_state.pdf_embeddings,
                        st.session_state.pdf_chunks,
                        top_k=3
                    )
                    answer = llm.generate_answer(question, chunks)
                
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })
                
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("👆 Upload a PDF to begin")
