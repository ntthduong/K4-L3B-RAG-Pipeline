import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="IELTS Writing RAG Chatbot",
    page_icon="✍️",
    layout="wide",
)


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.info("Không có nguồn được sử dụng.")
        return

    with st.expander(f"Nguồn đã dùng ({len(sources)})", expanded=True):
        for index, source in enumerate(sources, 1):
            metadata = source["metadata"]
            title = metadata.get("title", "Untitled")
            source_name = metadata.get("source", "unknown")
            url = metadata.get("url")
            score = source.get("score", 0.0)
            method = source.get("retrieval_method", "unknown")

            st.markdown(
                f"**[{index}] {title}**  \n"
                f"Source: `{source_name}` | Method: `{method}` | Score: `{score:.4f}`"
            )
            if url:
                st.markdown(f"URL: {url}")
            st.caption(source.get("content", "")[:500].replace("\n", " ") + "...")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("IELTS Writing RAG")
    st.caption("Chatbot trả lời câu hỏi IELTS Writing từ band descriptors, guide và bài viết tham khảo.")
    top_k = st.slider("Số chunks", 3, 10, 5)
    if st.button("Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()

st.title("IELTS Writing RAG Chatbot")
st.caption("Hỏi về IELTS Writing Task 1, Task 2, scoring criteria, band descriptors và writing tips.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))

query = st.chat_input("Ví dụ: What are the IELTS Writing assessment criteria?")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang retrieve context và tạo câu trả lời..."):
            try:
                result = generate_with_citation(query, top_k=top_k)
                answer = result["answer"]
                sources = result["sources"]
            except Exception as error:
                answer = f"Không thể tạo câu trả lời do lỗi hệ thống: {error}"
                sources = []

        st.markdown(answer)
        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
