#### AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA

from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import win32com.client
import datetime

prompt = "Tell me everything you are able to do"


def summarise(prompt):
    instruction = """You are an email summariser. You will receive a number of emails and i would like you to summarise the key points. You will do nothing else expect summarise emails.
    You will start your response with a list of the emails, the subjects and the senders. Then combining the content from all emails, you will write in bullet points key takeaways from the emails together under the following headings:
    Investment Strategy and Philosophy; Economics & Demographics; Politics, Policy and Regulation; Financial Markets; Psychology; Technologies; Sectors and Commodities; Companies; Valuation; Finance; Other. If there is no relevant content for one of the headings then just say NA
    Then give a final conclusion on the sentiment of the emails has changed over time (using the times of the emails) and what your key takeaways would be for a prudent investor.
    """
    client = genai.Client(api_key="AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA")
    model_id = "gemini-2.0-flash-exp"
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            response_modalities=["TEXT"],
            system_instruction=instruction
        )
    )
    return response.text

def get_recent_emails(folder_name):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    mailbox = outlook.Folders.Item(1)  # This is usually your primary mailbox
    # Access the "Blogs" folder
    folder = mailbox.Folders.Item(folder_name)
    messages = folder.Items
    messages.Sort("[ReceivedTime]", True)  # Sort by newest first
  

    if not messages:
        return []

    # Convert one_hour_ago to the same timezone as the emails
    first_email_time = messages.GetLast().ReceivedTime  # Get any email's datetime for timezone reference
    last_day = datetime.datetime.now(first_email_time.tzinfo) - datetime.timedelta(hours=100)

    recent_messages = [msg for msg in messages if msg.ReceivedTime >= last_day]
    
    email_texts = []

    for msg in recent_messages:
        try:
            email_text = f"Subject: {msg.Subject}\n{msg.ReceivedTime}\n{msg.Body}"
            email_texts.append(email_text)
        except Exception as e:
            print(f"Error reading email: {e}")

    return email_texts

def main():
    folder_name = "Blogs"  # Change if needed
    emails = get_recent_emails(folder_name)
   
    if not emails:
        print("No new emails in the last hour.")
        return
    
    combined_text = ""
    for email in emails:
        combined_text = combined_text + '\n'+ str(email)

    print(summarise(combined_text))

if __name__ == "__main__":
    main()

