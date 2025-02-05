#### AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA

from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Allows Gemini to 

def enable_lights():
    """Turn on the lighting system."""
    print("LIGHTBOT: Lights enabled.")


def set_light_color(rgb_hex: str):
    """Set the light color. Lights must be enabled for this to work."""
    print(f"LIGHTBOT: Lights set to {rgb_hex}.")


def stop_lights():
    """Stop flashing lights."""
    print("LIGHTBOT: Lights turned off.")


light_controls = [enable_lights, set_light_color, stop_lights]
instruction = "You are a helpful lighting system bot. You can turn lights on and off, and you can set the color. Do not perform any other tasks. You also know what HEX codes representing all colours/shades. Be very polite"

client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")
model_id = "gemini-2.0-flash-exp"
prompt = "Tell me everything you are able to do"

response = client.models.generate_content(
    model=model_id,
    contents=prompt,
    config=GenerateContentConfig(
        tools=light_controls,
        response_modalities=["TEXT"],
        system_instruction=instruction
    )
)

print(response.text)