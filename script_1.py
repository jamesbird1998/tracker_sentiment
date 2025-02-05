###### Model Options ######
#Model code	Base model	Replacement version
#gemini-2.0-flash-thinking-exp-1219	Gemini 2.0 Flash Thinking	gemini-2.0-flash-thinking-exp-01-21
#gemini-exp-1121	Gemini	gemini-exp-1206
#gemini-exp-1114	Gemini	gemini-exp-1206
#gemini-1.5-pro-exp-0827	Gemini 1.5 Pro	gemini-exp-1206
#gemini-1.5-pro-exp-0801	Gemini 1.5 Pro	gemini-exp-1206
#gemini-1.5-flash-8b-exp-0924	Gemini 1.5 Flash-8B	gemini-1.5-flash-8b
#gemini-1.5-flash-8b-exp-0827	Gemini 1.5 Flash-8B	gemini-1.5-flash-8b
#gemini-1.5-flash   Gemini 1.5 Flash
#gemini-1.5-pro     Gemini 1.5 Pro
#gemini-2.0-flash-exp   Gemini 2.0 Flash 

# Very basic use of Gemini

from google import genai

client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")
response = client.models.generate_content(
    model="gemini-2.0-flash-exp", contents="Hello"
)
print(response.text)


from google import genai

client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")

response = client.models.generate_content(model='gemini-2.0-flash-exp', contents='How does AI work?')
print(response.text)