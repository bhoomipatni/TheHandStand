"""
Translation Module using Google Generative AI (Gemini) with Service Account
"""

import os
from google.oauth2 import service_account
import google.generativeai as genai
from utils.config import get_gemini_api_key


class GeminiTranslator:
    def __init__(self):
        """Initialize Gemini with a Google Cloud Service Account."""
        self.service_account_path = get_gemini_api_key()  # Should return path/to/key.json
        self.model = None

        try:
            self.setup_authentication()
        except Exception as e:
            print(f"⚠️ Gemini service account setup failed: {e}")
            self.model = None

    def setup_authentication(self):
        """Configure Gemini using a service account JSON file."""
        if not self.service_account_path:
            raise ValueError("No service account path provided.")

        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(
                f"Service account file not found: {self.service_account_path}"
            )

        print("Setting up Google Gemini service account authentication...")

        # Load credentials from JSON file
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_path,
            scopes=["https://www.googleapis.com/auth/generative-language"]
        )

        # Configure Gemini
        genai.configure(credentials=credentials)
        self.model = genai.GenerativeModel("models/gemini-pro")

        print("Google Gemini configured using service account")

    # ===============================
    # TRANSLATE TEXT
    # ===============================
    def translate_text(self, text, target_language="es"):
        """Translate text using Gemini."""
        if not text or not text.strip() or not self.model:
            return ""

        lang_names = self.get_supported_languages()
        target_lang_name = lang_names.get(target_language, "Spanish")

        prompt = f"Translate this text to {target_lang_name}: '{text}'. Return only the translation."

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()

            return f"Translation to {target_lang_name}: {text}"

        except Exception as e:
            print(f"Translation error: {e}")
            return f"Translation to {target_lang_name}: {text}"

    # ===============================
    # IMPROVE ASL SENTENCE
    # ===============================
    def improve_sentence(self, asl_sentence):
        """Convert ASL-style sentence into natural English."""
        if not asl_sentence or not asl_sentence.strip() or not self.model:
            return asl_sentence

        # Skip single words
        if len(asl_sentence.split()) == 1:
            return asl_sentence

        prompt = f"""
Improve this ASL gesture sequence into natural English:
"{asl_sentence}"

Make it a clear, natural-sounding sentence. 
Use correct grammar and add missing connecting words.
Return ONLY the improved sentence.
"""

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                improved = response.text.strip().strip('"').strip("'")
                return improved if improved else asl_sentence

            return asl_sentence

        except Exception as e:
            print(f"Gemini sentence improvement error: {e}")
            return asl_sentence

    # ===============================
    # SUPPORTED LANGUAGES
    # ===============================
    def get_supported_languages(self):
        return {
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
