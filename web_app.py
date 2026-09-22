import streamlit as st
from ai_engine import get_available_models, stream_chat_response
from document_processor import process_multiple_files, format_documents_context
from search_service import search_live_web, format_search_context
from pdf_generator import generate_pdf_report
from auth_ui import render_auth_page
import database as db

# 1. Page Configuration
st.set_page_config(
    page_title="AI Intelligence & Societal Impact Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Check Authentication State
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    render_auth_page()
    st.stop()

# Current User Data
current_user = st.session_state.user
user_id = current_user["id"]
username = current_user["username"]

# 3. System Personas with Societal & Predictive Focus
PERSONAS = {
    "🌍 Societal Impact & Sustainability": "You are a visionary strategist focused on global societal progress, ethical AI, sustainable development, and positive community impact.",
    "🔮 Future Trends & Predictive Analyst": "You specialize in predictive analysis, forecasting technological, economic, and social shifts from historical foundations into the 2030s and beyond.",
    "🚀 Tech-for-Good & Innovation Advisor": "You help build high-impact technologies that empower people, enhance education, and solve real-world human challenges.",
    "💻 Senior Software Architect": "You are an expert software engineer and teacher. You explain complex code and architecture clearly with best practices.",
    "📊 Research & Data Analyst": "You are a rigorous data analyst. You synthesize findings, cite evidence, and identify key takeaways.",
    "📑 Executive Document Summarizer": "You extract key points, action items, and structured executive summaries suitable for immediate reporting.",
    "⚙️ Custom Persona": ""
}

# 4. Initialize Session State Variables
if "current_workspace_id" not in st.session_state:
    workspaces = db.get_user_workspaces(user_id)
    st.session_state.current_workspace_id = workspaces[0]["id"] if workspaces else None

if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_docs" not in st.session_state:
    st.session_state.processed_docs = []

if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""


# --- Helper to Switch Conversations ---
def load_conversation(conv_id):
    st.session_state.current_conv_id = conv_id
    db_messages = db.get_conversation_messages(conv_id)
    st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in db_messages]


# 5. Sidebar Interface
with st.sidebar:
    # User Profile Header
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        st.markdown(f"👤 **{username.capitalize()}**")
    with col_u2:
        if st.button("🚪", help="Sign Out"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.current_conv_id = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # --- WORKSPACE MANAGEMENT ---
    st.subheader("🏢 Workspaces")
    workspaces = db.get_user_workspaces(user_id)
    ws_options = {ws["id"]: ws["name"] for ws in workspaces}

    if st.session_state.current_workspace_id not in ws_options and workspaces:
        st.session_state.current_workspace_id = workspaces[0]["id"]

    selected_ws_id = st.selectbox(
        "Active Workspace",
        options=list(ws_options.keys()),
        format_func=lambda x: ws_options.get(x, "Unknown"),
        index=list(ws_options.keys()).index(st.session_state.current_workspace_id) if st.session_state.current_workspace_id in ws_options else 0,
        label_visibility="collapsed"
    )

    if selected_ws_id != st.session_state.current_workspace_id:
        st.session_state.current_workspace_id = selected_ws_id
        st.session_state.current_conv_id = None
        st.session_state.messages = []
        st.rerun()

    with st.expander("➕ Create New Workspace"):
        with st.form("new_ws_form", clear_on_submit=True):
            new_ws_name = st.text_input("Workspace Name")
            new_ws_desc = st.text_input("Description (Optional)")
            if st.form_submit_button("Create Workspace"):
                if new_ws_name.strip():
                    new_id = db.create_workspace(user_id, new_ws_name.strip(), new_ws_desc.strip())
                    st.session_state.current_workspace_id = new_id
                    st.session_state.current_conv_id = None
                    st.session_state.messages = []
                    st.success("Workspace created!")
                    st.rerun()

    st.markdown("---")

    # --- SEARCH PAST CHATS & HISTORY ---
    st.subheader("🔍 Search Chat History")
    search_query = st.text_input("Search messages", placeholder="Type keywords...", label_visibility="collapsed")
    
    if search_query.strip():
        search_results = db.search_messages(user_id, search_query, st.session_state.current_workspace_id)
        if search_results:
            st.caption(f"Found {len(search_results)} match(es):")
            for res in search_results:
                short_text = (res["content"][:55] + "...") if len(res["content"]) > 55 else res["content"]
                btn_label = f"💬 {res['conversation_title']}: {short_text}"
                if st.button(btn_label, key=f"search_{res['id']}", use_container_width=True):
                    load_conversation(res["conversation_id"])
                    st.rerun()
        else:
            st.caption("No matching messages found.")

    st.markdown("---")

    # --- CONVERSATION THREADS ---
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        st.subheader("💬 Conversations")
    with col_c2:
        if st.button("➕", help="Start a New Chat"):
            st.session_state.current_conv_id = None
            st.session_state.messages = []
            st.rerun()

    conv_list = db.get_conversations(user_id, st.session_state.current_workspace_id)
    if conv_list:
        for conv in conv_list:
            is_selected = (conv["id"] == st.session_state.current_conv_id)
            c1, c2 = st.columns([5, 1])
            with c1:
                prefix = "👉 " if is_selected else "🗨️ "
                if st.button(f"{prefix}{conv['title']}", key=f"conv_{conv['id']}", use_container_width=True):
                    load_conversation(conv["id"])
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{conv['id']}", help="Delete Chat"):
                    db.delete_conversation(conv["id"])
                    if st.session_state.current_conv_id == conv["id"]:
                        st.session_state.current_conv_id = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.caption("No conversations yet. Start chatting!")

    st.markdown("---")

    # --- REAL-TIME CAPABILITIES ---
    st.subheader("🌐 Live Knowledge & Web")
    enable_web_search = st.toggle("Live Web Search & Grounding", value=True, help="Fetches real-time internet information to keep answers fully up to date.")

    st.markdown("---")

    # --- AI MODEL & PERSONA SETTINGS ---
    st.subheader("⚙️ AI Configuration")
    available_models = get_available_models()
    default_idx = 0
    if "openai/gpt-oss-20b" in available_models:
        default_idx = available_models.index("openai/gpt-oss-20b")

    selected_model = st.selectbox(
        "AI Model",
        options=available_models,
        index=default_idx,
    )

    selected_persona_name = st.selectbox("Persona / Focus", list(PERSONAS.keys()))
    if selected_persona_name == "⚙️ Custom Persona":
        system_prompt = st.text_area(
            "Custom Instructions",
            value="You are a specialized AI assistant tailored to my needs."
        )
    else:
        system_prompt = PERSONAS[selected_persona_name]

    st.markdown("---")

    # --- MULTI-DOCUMENT UPLOADER ---
    st.subheader("📁 Reference Documents")
    uploaded_files = st.file_uploader(
        "Upload files (PDF, TXT, MD, CSV, PY)",
        type=["pdf", "txt", "md", "csv", "py"],
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Processing files..."):
            st.session_state.processed_docs = process_multiple_files(uploaded_files)
            st.session_state.doc_context = format_documents_context(st.session_state.processed_docs)

        total_words = sum(d["word_count"] for d in st.session_state.processed_docs)
        total_pages = sum(d["page_count"] for d in st.session_state.processed_docs)

        st.success(f"✅ Loaded {len(uploaded_files)} file(s)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total Pages", total_pages)
        with col_m2:
            st.metric("Total Words", f"{total_words:,}")

        with st.expander("📄 View Uploaded Files"):
            for doc in st.session_state.processed_docs:
                st.markdown(f"- **{doc['filename']}** ({doc['word_count']} words)")

        if st.button("✨ Summarize All Documents", use_container_width=True):
            summary_prompt = "Please provide a comprehensive summary of all uploaded documents, highlighting key insights, practical takeaways, and societal implications."
            st.session_state.messages.append({"role": "user", "content": summary_prompt})
            st.rerun()
    else:
        st.session_state.processed_docs = []
        st.session_state.doc_context = ""


# 6. Main Chat Area
current_ws_name = ws_options.get(st.session_state.current_workspace_id, "Workspace")

col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.title(f"🌍 {current_ws_name}")
with col_t2:
    if st.session_state.messages:
        # Full conversation PDF Export button
        full_chat_text = "\n\n".join([f"**{m['role'].upper()}**: {m['content']}" for m in st.session_state.messages])
        pdf_buffer = generate_pdf_report(
            title=f"Chat Report - {current_ws_name}",
            content=full_chat_text,
            workspace_name=current_ws_name,
            author=username.capitalize()
        )
        st.download_button(
            label="📥 Export PDF",
            data=pdf_buffer,
            file_name=f"Report_{current_ws_name}.pdf",
            mime="application/pdf",
            help="Download the entire chat as a formatted PDF report"
        )

# Document status banner
if st.session_state.processed_docs:
    st.info(f"📂 **Active Knowledge Base:** {len(st.session_state.processed_docs)} document(s) loaded. The AI will cite and analyze them.")

# Display Chat Messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If this is an assistant response, offer an instant PDF download
        if message["role"] == "assistant":
            resp_pdf = generate_pdf_report(
                title="AI Intelligence Report",
                content=message["content"],
                workspace_name=current_ws_name,
                author="AI Assistant"
            )
            st.download_button(
                label="📥 Download PDF",
                data=resp_pdf,
                file_name=f"AI_Report_{idx}.pdf",
                mime="application/pdf",
                key=f"dl_btn_{idx}",
                help="Download this response as a PDF document"
            )

# Quick Starters if conversation is fresh
if len(st.session_state.messages) == 0:
    st.chat_message("assistant").markdown(
        f"👋 **Welcome to your AI Societal & Predictive Intelligence Hub, {username.capitalize()}!**\n\n"
        f"I am equipped to analyze **past history**, synthesize **live real-time facts**, and provide **future projections & societal impact analysis**.\n\n"
        f"💡 **Try these quick starters or ask anything below:**"
    )
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if st.button("📈 AI: Past, Present & 2030 Projections", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Analyze the evolution of Artificial Intelligence: its foundational past, current present capabilities, and strategic future projections for the 2030s including its impact on society."})
            st.rerun()
    with col_s2:
        if st.button("🌍 Clean Energy & Future Sustainability", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Provide a comprehensive report on global clean energy transitions: historical energy patterns, latest present-day innovations, and future projections for societal sustainability."})
            st.rerun()
    with col_s3:
        if st.button("📑 Generate Executive PDF Report", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Generate an executive report on the top global technology and societal trends shaping our future. Format it cleanly with key takeaways."})
            st.rerun()

# 7. Chat Input Handling
user_input = st.chat_input("Ask a question, request future forecasts, or say 'generate into pdf'...")

trigger_response = False
if user_input:
    # Ensure active conversation exists in DB
    if st.session_state.current_conv_id is None:
        title = (user_input[:35] + "...") if len(user_input) > 35 else user_input
        conv_id = db.create_conversation(user_id, st.session_state.current_workspace_id, title)
        st.session_state.current_conv_id = conv_id

    st.session_state.messages.append({"role": "user", "content": user_input})
    db.save_message(st.session_state.current_conv_id, "user", user_input)

    with st.chat_message("user"):
        st.markdown(user_input)
    trigger_response = True

elif len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    trigger_response = True
    if st.session_state.current_conv_id is None:
        title = "Intelligence Report"
        conv_id = db.create_conversation(user_id, st.session_state.current_workspace_id, title)
        st.session_state.current_conv_id = conv_id
        db.save_message(st.session_state.current_conv_id, "user", st.session_state.messages[-1]["content"])

if trigger_response:
    with st.chat_message("assistant"):
        # Perform live web search if enabled
        search_context = ""
        if enable_web_search and len(st.session_state.messages) > 0:
            last_user_msg = st.session_state.messages[-1]["content"]
            with st.spinner("🌐 Grounding with real-time web knowledge..."):
                search_results = search_live_web(last_user_msg, max_results=3)
                search_context = format_search_context(search_results)

        # Stream response
        response_stream = stream_chat_response(
            messages=st.session_state.messages,
            model=selected_model,
            system_prompt=system_prompt,
            document_context=st.session_state.doc_context,
            search_context=search_context
        )
        full_response = st.write_stream(response_stream)

        # Render instant PDF download button for this response
        resp_pdf = generate_pdf_report(
            title="AI Intelligence Report",
            content=full_response,
            workspace_name=current_ws_name,
            author="AI Assistant"
        )
        st.download_button(
            label="📥 Download as PDF",
            data=resp_pdf,
            file_name=f"AI_Report_{len(st.session_state.messages)}.pdf",
            mime="application/pdf",
            help="Download this response as a PDF document"
        )

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    db.save_message(st.session_state.current_conv_id, "assistant", full_response)
