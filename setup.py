"""JARVIS-X Enhanced Setup Script"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("           🤖 JARVIS-X ENHANCED SETUP")
    print("    Your Personal AI Operating System with Free APIs")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required!")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        return False

    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create virtual environment."""
    print("\\n📦 Setting up virtual environment...")

    if os.path.exists(".venv"):
        print("   Virtual environment already exists.")
        return True

    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment.")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("\\n📚 Installing dependencies...")

    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(".venv", "Scripts", "pip")
    else:  # Unix/Linux/macOS
        pip_path = os.path.join(".venv", "bin", "pip")

    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Setup environment configuration file."""
    print("\\n⚙️  Setting up environment configuration...")

    if os.path.exists(".env"):
        print("   .env file already exists.")
        response = input("   Do you want to recreate it? (y/N): ").lower()
        if response != 'y':
            return True

    if os.path.exists(".env.template"):
        shutil.copy(".env.template", ".env")
        print("✅ Created .env file from template.")
        print("   📝 Please edit .env file and add your API keys.")
        return True
    else:
        # Create basic .env file
        basic_env = '''# JARVIS-X Basic Configuration
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
ASSISTANT_NAME=Jarvis
WAKE_WORD=jarvis
'''
        with open(".env", "w") as f:
            f.write(basic_env)
        print("✅ Created basic .env file.")
        print("   📝 Please edit .env file and add your API keys.")
        return True

def create_directories():
    """Create necessary directories."""
    print("\\n📁 Creating directories...")

    directories = [
        "logs",
        "data",
        "temp",
        "exports"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("✅ Directories created successfully!")
    return True

def test_installation():
    """Test the installation."""
    print("\\n🧪 Testing installation...")

    try:
        # Test imports
        import google.generativeai
        import requests
        import pyttsx3
        print("✅ Core dependencies working!")

        # Test API manager
        from core.api_manager import SyncAPIManager
        api_manager = SyncAPIManager()
        print("✅ API manager working!")

        # Test skills
        from skills.entertainment import EntertainmentSkill
        from skills.information import InformationSkill
        from skills.productivity import ProductivitySkill
        print("✅ Enhanced skills working!")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_api_setup_guide():
    """Show guide for setting up free APIs."""
    print("\\n" + "=" * 60)
    print("           🔑 FREE API SETUP GUIDE")
    print("=" * 60)

    apis = [
        {
            "name": "Google Gemini AI (REQUIRED)",
            "url": "https://makersuite.google.com/app/apikey",
            "description": "Core AI functionality - completely free!",
            "env_var": "GEMINI_API_KEY"
        },
        {
            "name": "News API",
            "url": "https://newsapi.org/",
            "description": "1000 requests/day free - latest news",
            "env_var": "NEWS_API_KEY"
        },
        {
            "name": "OpenWeatherMap",
            "url": "https://openweathermap.org/api",
            "description": "1000 calls/day free - weather data",
            "env_var": "WEATHER_API_KEY"
        },
        {
            "name": "Telegram Bot",
            "url": "https://t.me/BotFather",
            "description": "Completely free - chat with @BotFather",
            "env_var": "TELEGRAM_BOT_TOKEN"
        }
    ]

    for i, api in enumerate(apis, 1):
        print(f"\\n{i}. {api['name']}")
        print(f"   🌐 URL: {api['url']}")
        print(f"   📝 Description: {api['description']}")
        print(f"   🔧 Environment Variable: {api['env_var']}")

    print("\\n" + "=" * 60)
    print("💡 TIP: Many features work without API keys!")
    print("   - Jokes, quotes, facts, crypto prices are completely free")
    print("   - Only Gemini AI key is required for core functionality")
    print("=" * 60)

def show_usage_examples():
    """Show usage examples."""
    print("\\n" + "=" * 60)
    print("           🎯 USAGE EXAMPLES")
    print("=" * 60)

    examples = [
        "🎭 Entertainment: 'Tell me a joke', 'Give me a quote', 'Random fact'",
        "📰 Information: 'Weather in London', 'Latest tech news', 'Bitcoin price'",
        "📋 Productivity: 'Add task: Buy groceries', 'Remind me in 1 hour', 'List my tasks'",
        "🖥️  System: 'Open Chrome', 'What time is it?', 'Help'",
        "💬 Chat: 'Hello Jarvis', 'How are you?', 'What can you do?'"
    ]

    for example in examples:
        print(f"   {example}")

    print("\\n💡 Just speak naturally - JARVIS understands context!")

def main():
    """Main setup function."""
    print_banner()

    # Check Python version
    if not check_python_version():
        return False

    # Create virtual environment
    if not create_virtual_environment():
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    # Setup environment file
    if not setup_environment_file():
        return False

    # Create directories
    if not create_directories():
        return False

    # Test installation
    if not test_installation():
        print("\\n⚠️  Installation test failed, but setup completed.")
        print("   You may need to activate the virtual environment and install dependencies manually.")

    # Show guides
    show_api_setup_guide()
    show_usage_examples()

    print("\\n" + "=" * 60)
    print("           ✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\\n🚀 Next steps:")
    print("   1. Edit .env file and add your API keys")
    print("   2. Activate virtual environment:")
    if os.name == 'nt':
        print("      .venv\\\\Scripts\\\\activate")
    else:
        print("      source .venv/bin/activate")
    print("   3. Run JARVIS: python main.py")
    print("\\n🎉 Welcome to the future of AI assistance!")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n\\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\n❌ Setup failed with error: {e}")
        sys.exit(1)
