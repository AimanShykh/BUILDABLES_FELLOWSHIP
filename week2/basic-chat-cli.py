import os 
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() 

class SimpleChatBot:
    def __init__(self, api_key: str):
        """Initialize chatbot with api key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash") 
        self.conversation_history = [] # Additional feature: store history
        self.system_prompt = "You are a helpful AI assistant."


        
    def set_system_prompt(self, prompt: str):
        """Set or update the system prompt"""
        self.system_prompt = prompt
        print(f"✅ System prompt updated: {prompt[:50]}...")
    
    def get_response(self, user_input: str) -> str:
        """Get response from Gemini API"""
        conversation_text = f"System: {self.system_prompt}\n"
        for msg in self.conversation_history:
            role = "User" if msg["role"] == "user" else "Assistant" 
            conversation_text += f"{role}: {msg['content']}\n"
        conversation_text += f"User: {user_input}\nAssistant:"

        try:
            response = self.model.generate_content(conversation_text)
            ai_response = response.text.strip()

            # Save history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return ai_response

        except Exception as e:
            return f"❌ Error: {str(e)}"
        
    def save_conversation(self, filename: str = None):
        """Save conversation to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "system_prompt": self.system_prompt,
            "conversation": self.conversation_history
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(conversation_data, f, indent=2)
            print(f"💾 Conversation saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("📭 No conversation history yet.")
            return
        
        print("\n" + "="*50)
        print("📜 CONVERSATION HISTORY")
        print("="*50)
        
        for i, message in enumerate(self.conversation_history, 1):
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                print(f"\n👤 User ({i//2 + 1}):")
                print(f"   {content}")
            else:
                print(f"\n🤖 Assistant ({i//2}):")
                print(f"   {content}")
        
        print("\n" + "="*50)

def compare_personas(api_key: str, user_input: str):
    """Ask the same question to all personas and compare responses."""
    presets = get_system_prompt_presets()

    print("\n📊 COMPARISON RESULTS")
    print("=" * 60)

    for key, (name, prompt) in presets.items():

        chatbot = SimpleChatBot(api_key) # New instance for each persona
        chatbot.set_system_prompt(prompt)
        chatbot.conversation_history = []  # Refreshing history

        response = chatbot.get_response(user_input)

        print(f"\n👤 Persona: {name}")
        print("-" * 60)
        print(response)


def get_system_prompt_presets():
    """Return predefined system prompts"""
    return {
      
       "1": ("Professional Assistant", "You are a professional business consultant. Provide formal strategic advice, market insights, and practical business solutions.")  ,
       "2": ("Creative Companion","You are a creative writing assistant. Help with brainstorming, storytelling, and creative projects. Be imaginative and artistic."),
       "3": ("Technical Expert", "You are a technical expert. Provide detailed, accurate technical information with step-by-step explanations.")
       
    }

def display_help():
    """Display available commands"""
    print("\n" + "="*50)
    print("🤖 CHATBOT COMMANDS")
    print("="*50)
    print("💬 Just type your message to chat")
    print("📝 /system    - Change system prompt")
    print("📜 /history   - Show conversation history")  
    print("💾 /save      - Save conversation to file")
    print("💾 /compare   - Compare different System Prompts")
    print("🧹 /clear     - Clear conversation history")
    print("❓ /help      - Show this help message")
    print("🚪 /exit      - Exit the chatbot")
    print("="*50)

def main():
    print("🤖 Welcome to the Simple ChatBot!")
    print("="*40)
    
    # Getting API key
    api_key = os.getenv("API_KEY")
    if not api_key:
        api_key = input("🔑 Please enter your API key: ").strip()
        if not api_key:
            print("❌ API key is required to continue.")
            return
    
    # Initializing chatbot
    try:
        chatbot = SimpleChatBot(api_key)
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        return
    
    display_help()
    print(f"\n💡 Current system prompt: {chatbot.system_prompt}")
    print("\n🚀 Ready to chat! Type your message or use commands starting with '/'")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handling commands for chatbot
            if user_input.startswith('/'):
                command = user_input[1:].lower()
                
                if command == 'exit':
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    display_help()

                elif command == 'compare':
                    question = input("Enter your question to compare: ").strip()
                    if question:
                        compare_personas(api_key, question)

                
                elif command == 'clear':
                    chatbot.conversation_history = []
                    print("🧹 Conversation history cleared!")
                
                elif command == 'history':
                    chatbot.show_history()
                
                elif command == 'system':
                    print("\n📝 SYSTEM PROMPT OPTIONS:")
                    presets = get_system_prompt_presets()
                    for key, (name, _) in presets.items():
                        print(f"   {key}. {name}")
                    print("   4. custom. (Enter your own prompt)")
                    
                    choice = input("\nChoose option (1-3 or 'custom'): ").strip()
                    
                    if choice in presets:
                        name, prompt = presets[choice]
                        chatbot.set_system_prompt(prompt)
                        print(f"✅ Switched to: {name}")
                    elif choice.lower() == 'custom':
                        custom_prompt = input("Enter your custom system prompt: ").strip()
                        if custom_prompt:
                            chatbot.set_system_prompt(custom_prompt)
                    else:
                        print("❌ Invalid choice.")
                
                elif command == 'save':
                    filename = input("Enter filename (press Enter for auto-generated): ").strip()
                    filename = filename if filename else None
                    chatbot.save_conversation(filename)
                
                elif command == 'load':
                    filename = input("Enter filename to load: ").strip()
                    if filename:
                        chatbot.load_conversation(filename)
                
                else:
                    print(f"❌ Unknown command: {command}. Type '/help' for available commands.")
            
            else:
                # Regular chat message
                print("\n🤖 Assistant:", end=" ")
                response = chatbot.get_response(user_input)
                print(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()