## Uses gemini which google search confirmations

from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")
model_id = "gemini-2.0-flash-exp"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

response = client.models.generate_content(
    model=model_id,
    contents="When is the next total solar eclipse in the United States?",
    config=GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
    )
)

for each in response.candidates[0].content.parts:
    print(each.text)
# Example response:
# The next total solar eclipse visible in the contiguous United States will be on ...