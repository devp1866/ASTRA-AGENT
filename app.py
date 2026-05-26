
import streamlit as st
from utils.agent_core import handle_query_with_memory
from utils.memory_manager import create_new_session, get_recent_messages, clear_session
import time

st.set_page_config(
    page_title="ASTRA | Advanced Support & Task Response Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# GLOBAL CSS STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Outfit', sans-serif; }
    
    /* Advanced Dark Theme with Layout Redesign */
    :root {
        --bg-color: #0e1117;
        --surface-color: #1a1c23;
        --user-msg: #2b52ff;
        --bot-msg: #212529;
        --text-primary: #ffffff;
        --text-secondary: #a0a5b1;
        --accent: #00d2ff;
    }
    
    .stApp { background-color: var(--bg-color); color: var(--text-primary); }
    #MainMenu, footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* Header layout redesign - floating island */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        margin: 1rem auto 2rem auto;
        background: var(--surface-color);
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .app-header h1 { font-size: 1.4rem; margin: 0; color: var(--text-primary); font-weight: 600; padding: 0;}
    .app-header p { margin: 0; color: var(--accent); font-size: 0.9rem; font-weight: 500; }
    
    /* Chat Layout Redesign */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 1.5rem;
        display: flex !important;
        gap: 1rem !important;
    }
    
    /* User Message - Right aligned */
    [data-testid="stChatMessage"][data-testid-role="user"] {
        flex-direction: row-reverse;
    }
    
    [data-testid="stChatMessage"][data-testid-role="user"] .stMarkdown {
        background: var(--user-msg);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 4px 20px;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(43, 82, 255, 0.3);
    }
    
    /* Assistant Message - Left aligned */
    [data-testid="stChatMessage"][data-testid-role="assistant"] .stMarkdown {
        background: var(--bot-msg);
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 4px;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Fix markdown width inside bubbles */
    [data-testid="stChatMessage"] .stMarkdown p {
        margin: 0 !important;
    }
    
    /* Floating Chat Input Redesign */
    [data-testid="stChatInput"] {
        background: var(--surface-color) !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6) !important;
        padding: 0.5rem 1rem !important;
        margin-bottom: 1rem;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent) !important;
    }
    
    /* Welcome Card completely redesigned */
    .welcome-card {
        text-align: center;
        padding: 4rem 2rem;
        background: radial-gradient(circle at center, rgba(26,28,35,0.8) 0%, transparent 100%);
        border: none;
        box-shadow: none;
        margin-top: 2rem;
    }
    .welcome-card h3 { font-size: 2.5rem; color: var(--text-primary); margin-bottom: 1rem; }
    .welcome-card p.subtitle { font-size: 1.1rem; color: var(--text-secondary); max-width: 600px; margin: 0 auto 2.5rem auto; line-height: 1.6;}
    .features-grid {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .feature-pill {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        color: var(--text-primary);
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: transform 0.2s ease;
    }
    .feature-pill:hover {
        transform: translateY(-3px);
        border-color: var(--accent);
    }
    
    /* Sidebar Redesign */
    [data-testid="stSidebar"] {
        background: #111318 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] button {
        background: transparent !important;
        border: 1px solid var(--accent) !important;
        color: var(--accent) !important;
        border-radius: 50px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: var(--accent) !important;
        color: black !important;
    }
    .status-badge {
        background: transparent !important;
        border: none !important;
        border-left: 3px solid !important;
        border-radius: 0 !important;
        padding: 0.5rem 1rem !important;
        text-align: left !important;
        display: block !important;
        margin-bottom: 1rem !important;
    }
    .status-active { border-color: #00ff88 !important; color: #00ff88 !important; }
    .status-ended { border-color: #ff3366 !important; color: #ff3366 !important; }
    .status-messages { border-color: var(--accent) !important; color: var(--text-primary) !important; }
    
    .stInfo {
        background: rgba(43, 82, 255, 0.1) !important;
        border-left: 4px solid var(--user-msg) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# SESSION INITIALIZATION 
if "session_id" not in st.session_state:
    st.session_state.session_id = create_new_session()
    clear_session(st.session_state.session_id)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = True

# SIDEBAR 
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>ASTRA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e;'>Smart AI Assistance</p>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🆕 Start New Session", use_container_width=True):
        clear_session(st.session_state.session_id)
        st.session_state.session_id = create_new_session()
        st.session_state.messages = []
        st.session_state.conversation_active = True
        st.rerun()
    
    st.divider()
    st.subheader("Session Stats")
    message_count = len(st.session_state.messages) // 2 if len(st.session_state.messages) > 0 else 0
    
    if st.session_state.conversation_active:
        st.markdown('<div class="status-badge status-active">🟢 Status: Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-ended">🔴 Status: Ended</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="status-badge status-messages">💬 Messages: {message_count}</div>', unsafe_allow_html=True)

# MAIN HEADER 
st.markdown("""
<div class="app-header">
    <h1>ASTRA</h1>
    <p>Intelligent Support Agent</p>
</div>
""", unsafe_allow_html=True)

# QUICK TIP
st.info("💡 Quick Tip: Type 'exit', 'quit', 'end', or 'bye' to end the conversation.")

# WELCOME MESSAGE 
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-card">
        <h3>ASTRA AI</h3>
        <p class="subtitle">I'm your intelligent support assistant. How can I help you today?</p>
        <div class="features-grid">
            <div class="feature-pill">💡 General Support</div>
            <div class="feature-pill">🔧 Technical Issues</div>
            <div class="feature-pill">💳 Billing & Payments</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CONVERSATION STATUS 
if not st.session_state.conversation_active:
    st.info("💡 The conversation has ended. Click '🆕 Start New Session' in the sidebar to begin a new conversation.")

# CHAT INTERFACE 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# USER INPUT HANDLING 
if st.session_state.conversation_active:
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Check for exit commands
        if user_input.lower().strip() in ["exit", "quit", "bye", "end"]:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            farewell_msg = "👋 Thank you for using ASTRA! The conversation has ended. Click '🆕 Start New Session' in the sidebar to start a new conversation."
            with st.chat_message("assistant"):
                st.markdown(farewell_msg)
            st.session_state.messages.append({"role": "assistant", "content": farewell_msg})
            st.session_state.conversation_active = False
            st.rerun()
        
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            try:
                result = handle_query_with_memory(st.session_state.session_id, user_input)
                response = result["response"]
            except Exception as e:
                # Security: Sanitize error output so internal paths or DB errors don't leak
                print(f"Internal error during chat processing: {str(e)}")
                response = "⚠️ I'm sorry, I encountered an internal error processing your request. Please try again later."
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
else:
    st.chat_input("Type your message here...", disabled=True)

# SEO INJECTION (SAFE)
import streamlit.components.v1 as components
components.html(
    """
    <script>
        try {
            const head = window.parent.document.head;
            const addMeta = (name, content, isProperty=false) => {
                const meta = window.parent.document.createElement('meta');
                if (isProperty) {
                    meta.setAttribute('property', name);
                } else {
                    meta.setAttribute('name', name);
                }
                meta.setAttribute('content', content);
                head.appendChild(meta);
            };
            addMeta('description', 'ASTRA - Intelligent Support Agent providing 24/7 automated assistance.');
            addMeta('keywords', 'AI, Customer Support, Streamlit, ASTRA');
            addMeta('og:title', 'ASTRA Support Agent', true);
            addMeta('og:description', 'Automated customer support using advanced AI.', true);
        } catch (e) {
            // Silently fail if cross-origin iframe policies block parent access
            console.log("SEO injection skipped due to iframe restrictions.");
        }
    </script>
    """,
    height=0,
    width=0
)