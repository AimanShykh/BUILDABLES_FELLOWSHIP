"""
Streamlit Chatbot with Gemini Integration

"""

import streamlit as st
import json
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

MEMORY_FILE = "chat_memory.json"

def load_memory():
    """Load chat memory from file if it exists"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []



def save_memory(history):
    """Save chat memory to file"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)



st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)





load_dotenv() 



class ChatBot:
    def __init__(self):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found. Did you set it in your .env file?")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def get_response(self, messages):
        try:
            # Convert messages (list of dicts) into a string prompt
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"




def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful AI assistant."

def get_system_prompts():
    """Predefined system prompts for different personas"""
    return {
      
        "Professional Assistant": "You are a professional business consultant. Provide formal strategic advice, market insights, and practical business solutions." ,
        "Creative Companion":"You are a creative writing assistant. Help with brainstorming, storytelling, and creative projects. Be imaginative and artistic.",
        "Technical Expert": "You are a technical expert. Provide detailed, accurate technical information with step-by-step explanations."
    }

def export_chat_history():
    """Export chat history as JSON"""
    if st.session_state.chat_history:
        export_data = {
            "export_date": datetime.now().isoformat(),
            "system_prompt": st.session_state.system_prompt,
            "conversation": st.session_state.chat_history
        }
        return json.dumps(export_data, indent=2)
    return None

def main():
    
    st.title("AssistAI 🤖")
   
    
    # Initialize
    initialize_session_state()
    chatbot = ChatBot()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System prompt selection
        system_prompts = get_system_prompts()
        selected_persona = st.selectbox(
            "Choose AI Persona:",
            list(system_prompts.keys()),
            key="persona_select"
        )
        
        # Update system prompt when persona changes
        if st.session_state.system_prompt != system_prompts[selected_persona]:
            st.session_state.system_prompt = system_prompts[selected_persona]
           
        
        # Display current system prompt
        with st.expander("View System Prompt"):
            st.text_area(
                "Current System Prompt:",
                value=st.session_state.system_prompt,
                height=100,
                disabled=True
            )
        
        # Chat controls
        st.header("💬 Chat Controls")
        
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
        
        # Export functionality
        if st.session_state.chat_history:
            if st.button("Export Chat History"):
                export_data = export_chat_history()
                if export_data:
                    st.download_button(
                        "Download JSON",
                        export_data,
                        f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json"
                    )
        
        # Statistics
        st.header("📊 Statistics")
        st.metric("Messages Sent", len([m for m in st.session_state.chat_history if m["role"] == "user"]))
        st.metric("AI Responses", len([m for m in st.session_state.chat_history if m["role"] == "assistant"]))
    
    # Main chat interface
    st.header("What would you like to ask?")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message["role"] == "assistant":
                    st.caption(f"Generated at {message.get('timestamp', 'Unknown time')}")
    
    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Add user message to history
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.chat_history.append(user_message)
        save_memory(st.session_state.chat_history)  # persist

        # Display user message
        with st.chat_message("user"):
            st.write(user_input)

        # Prepare messages for API call
        api_messages = [
            {"role": "system", "content": st.session_state.system_prompt}
        ]
        recent_messages = st.session_state.chat_history[-10:]
        for msg in recent_messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.get_response(api_messages)
                st.write(response)
                st.caption(f"Generated at {datetime.now().strftime('%H:%M:%S')}")

        # Add assistant response
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.chat_history.append(assistant_message)
        save_memory(st.session_state.chat_history)  # persist
        st.rerun()

    with st.expander("💡 Usage Tips"):
        st.markdown("""
        **How to get the best responses:**
        1. **Be specific** - Clear questions get better answers
        2. **Provide context** - Help the AI understand your situation
        3. **Try different personas** - Each has different strengths
        4. **Iterate** - Refine your questions based on responses
        
        **Experiment with system prompts:**
        - Notice how different personas respond differently to the same question
        - Try asking the same question with different personas
        - Observe changes in tone, detail level, and approach
        """)


    

if __name__ == "__main__":
    main()