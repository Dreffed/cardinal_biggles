"""
Test script to verify LLM Factory setup
"""

import asyncio
import os
from pathlib import Path


async def test_ollama():
    """Test Ollama connection"""
    print("\n🧪 Testing Ollama...")

    try:
        from core.llm_factory import LLMFactory

        # Create test config
        test_config = """
llm:
  default_provider: "ollama"
  default_model: "llama3.1"

  providers:
    ollama:
      base_url: "http://localhost:11434"
      models:
        standard: "llama3.1"
      default_temperature: 0.1
      timeout: 120

agents:
  test_agent:
    provider: "ollama"
    model: "llama3.1"
    temperature: 0.1
"""

        # Save test config
        Path("config").mkdir(exist_ok=True)
        Path("config/test_config.yaml").write_text(test_config)

        # Create factory
        factory = LLMFactory("config/test_config.yaml")

        # Create Ollama LLM
        llm = factory.create_llm(provider="ollama", model="llama3.1")

        print(f"✓ Ollama LLM created: {type(llm).__name__}")

        # Test invoke
        print("  Testing invoke...")
        response = await llm.ainvoke("Say 'test successful' and nothing else")
        print(f"  Response: {response.content}")

        return True

    except Exception as e:
        print(f"✗ Ollama test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_imports():
    """Test which LangChain packages are available"""
    print("\n📦 Checking available packages...\n")

    imports = {
        "langchain_ollama.ChatOllama": None,
        "langchain_community.chat_models.ChatOllama": None,
        "langchain_community.llms.Ollama": None,
        "langchain_openai.ChatOpenAI": None,
        "langchain_anthropic.ChatAnthropic": None,
    }

    for import_path in imports.keys():
        try:
            module_path, class_name = import_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            imports[import_path] = "✓ Available"
            print(f"✓ {import_path}")
        except ImportError:
            imports[import_path] = "✗ Not installed"
            print(f"✗ {import_path}")
        except Exception as e:
            imports[import_path] = f"✗ Error: {e}"
            print(f"✗ {import_path} - {e}")

    return imports


async def main():
    """Run all tests"""
    print("="*60)
    print("Cardinal Biggles - LLM Factory Test")
    print("="*60)

    # Test imports
    imports = await test_imports()

    # Test Ollama if available
    if any("ollama" in k.lower() and "✓" in v for k, v in imports.items()):
        await test_ollama()
    else:
        print("\n⚠️  No Ollama packages found. Install with:")
        print("   pip install langchain-ollama")
        print("   or")
        print("   pip install langchain-community")

    print("\n" + "="*60)
    print("Tests complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
