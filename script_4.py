## This allows realtime control of lights via functions


from google import genai
from google.genai.types import FunctionResponse, GenerateContentConfig

# ✅ Store the light system status
light_status = {
    "enabled": False,  # Whether lights are ON or OFF
    "color": None  # Stores the HEX colour if set
}

# ✅ Initialize Gemini API client
client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")
model_id = "gemini-2.0-flash-exp"

# ✅ Define functions for light control
def enable_lights():
    """Turn on the lighting system."""
    if not light_status["enabled"]:
        light_status["enabled"] = True
        print("LIGHTBOT: Lights enabled.")
    else:
        print("LIGHTBOT: Lights are already on.")
    return {"status": "Lights enabled"}

def set_light_color(rgb_hex: str):
    """Set the light color. Lights must be enabled for this to work."""
    if light_status["enabled"]:
        light_status["color"] = rgb_hex
        print(f"LIGHTBOT: Lights set to {rgb_hex}.")
        return {"status": f"Lights set to {rgb_hex}"}
    else:
        print("LIGHTBOT: Cannot set colour. Lights are off.")
        return {"status": "Cannot set color. Lights are off."}

def stop_lights():
    """Turn off the lighting system."""
    if light_status["enabled"]:
        light_status["enabled"] = False
        light_status["color"] = None
        print("LIGHTBOT: Lights turned off.")
        return {"status": "Lights turned off"}
    else:
        print("LIGHTBOT: Lights are already off.")
        return {"status": "Lights already off"}

light_controls = [enable_lights, set_light_color, stop_lights]

# ✅ Register functions with Gemini
tools = light_controls

# ✅ Start interactive chatbot loop
print("\nLIGHTBOT: Hello! I can control the lights. Type 'exit' to stop.")

while True:
    # ✅ Update Gemini's system instruction with real-time light status
    instruction = f"""You are a helpful lighting system bot. 
    You can turn lights on and off, and set their color. 
    Current light status: {'ON' if light_status['enabled'] else 'OFF'}
    Current light color: {light_status['color'] if light_status['color'] else 'None'}.
    Only respond politely about lighting controls. Do not perform other tasks.
    You know all the hexcodes for all colours
    """

    # ✅ Get user input
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        print("LIGHTBOT: Goodbye!")
        break

    # ✅ Send request to Gemini
    response = client.models.generate_content(
        model=model_id,
        contents=user_input,
        config=GenerateContentConfig(
            tools=tools,
            response_modalities=["TEXT"],
            system_instruction=instruction
        )
    )

    print(response.text)

    
