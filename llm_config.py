"""
LLM configuration and initialization supporting multiple providers.
"""
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()


def get_llm() -> Any:
    """
    Initialize and return the LLM based on environment configuration.
    Supports OpenAI, Anthropic (Claude), and can be extended for Google.
    """
    provider = os.getenv("MODEL_PROVIDER", "openai").lower()
    model_name = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.2,
            streaming=False
        )
        print(f"✓ Initialized OpenAI LLM: {model_name}")
        return llm
    
    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            
            llm = ChatAnthropic(
                model=model_name,
                temperature=0.2,
                max_tokens=4096
            )
            print(f"✓ Initialized Anthropic LLM: {model_name}")
            return llm
        except ImportError:
            raise ImportError(
                "Anthropic support requires: pip install langchain-anthropic"
            )
    
    elif provider == "google":
        # Placeholder for Google Gemini integration
        # You would need to install: pip install langchain-google-genai
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.2
            )
            print(f"✓ Initialized Google LLM: {model_name}")
            return llm
        except ImportError:
            raise ImportError(
                "Google support requires: pip install langchain-google-genai"
            )
    
    else:
        raise ValueError(
            f"Unsupported MODEL_PROVIDER: {provider}. "
            f"Supported providers: openai, anthropic, google"
        )


def get_embeddings() -> Any:
    """
    Get embeddings model (currently using OpenAI).
    Can be extended to support other providers.
    """
    from langchain_openai import OpenAIEmbeddings
    
    return OpenAIEmbeddings()

