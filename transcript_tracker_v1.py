# Import necessary packages
import os
import re
import json
from PyPDF2 import PdfReader
import pandas as pd
import json
import ace_tools_open as tools
from google import genai
from google.genai.types import GenerateContentConfig
import time as tm

# My Google Gemini API key
API_KEY = "AIzaSyD_OKBIvvr_MFt231XsBm7iDBZe8m3r8LA"

# Initialize Google AI client
client = genai.Client(api_key=API_KEY)
model_id = "gemini-2.0-flash-exp"

# Function to extract the quarter from a transcript filename 
# Requires the filename to have a date in the name of the form yyyy-mm-dd (CapIQ does this...not sure about Bloomberg)
def extract_quarter_from_filename(filename):
    """Extracts the actual quarter being reported based on the filename date (shifting back by one quarter)."""
    date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(date_pattern, filename)
    if match:
        year, month, _ = map(int, match.groups())
        if month in [1, 2, 3]:  # Q1 earnings call -> previous year's Q4. Dates of earnings are always in the quarter after the actual quarter.
            quarter = "Q4"
            year -= 1
        elif month in [4, 5, 6]:  # Q2 earnings call -> Q1 of the same year
            quarter = "Q1"
        elif month in [7, 8, 9]:  # Q3 earnings call -> Q2 of the same year
            quarter = "Q2"
        else:  # Q4 earnings call -> Q3 of the same year
            quarter = "Q3"
        return f"{quarter} {year}"
    return None  # Return None if no valid date found

# Function to extract text content from PDFs 
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file) 
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n" #Extracts text from a single PDF file.
        return text

# Function to extract text from all transcripts in a given folder e.g. dassault_transcripts 
def extract_text_from_folder(folder_name):
    quarterly_data = {}
    for filename in os.listdir(folder_name):
        if filename.lower().endswith(".pdf"):
            quarter = extract_quarter_from_filename(filename)
            if quarter:
                pdf_path = os.path.join(folder_name, filename)
                transcript_text = extract_text_from_pdf(pdf_path)

                if quarter in quarterly_data:
                    quarterly_data[quarter] += "\n\n" + transcript_text  # Append if multiple PDFs per quarter
                else:
                    quarterly_data[quarter] = transcript_text
    return quarterly_data

# Function to ensure that whatever Geminini generates is in fact in JSON format and convert if necessary
def extract_json_from_text(text):
    json_pattern = r"```json\n(.*?)\n```"  # Match JSON enclosed in triple backticks
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()  # Extract JSON without backticks
        try:
            return json.loads(json_str)  # Convert to dictionary
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None  # Return None if parsing fails
    return None  # Return None if no valid JSON found

#Summarises each quarter's transcript using AI.
def summarise(quarterly_data):
    results = {}
    for quarter, transcript in quarterly_data.items():
        prompt = f"Extract insights for {quarter}:\n\n{transcript}"
        instruction = """
        ONLY return valid JSON. Do NOT add any explanations, titles, or extra text.

        Format your response EXACTLY like this: 

        ```json
        {
            "top_positive_themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
            "top_negative_themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
            "future_sentiment_score": X,
            "future_sentiment_comment": "Outlook is moderately positive due to strong bookings.",
            "present_sentiment_score": Y,
            "present_sentiment_comment": "Solid revenue growth but margin compression.",
            "analysts_sentiment_score": Z,
            "analysts_sentiment_comment": "Analysts tend to ask questions about positives not negatives."
        }

        Sentiment scores are numbers out of 100.
        For sentiment comments, mention specific products and services where possible.
        For analyst sentiment, this is the sentiment from the questions asked by the analysts. 
        """
        # Run Gemini for given transcipt and instruction set
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
                system_instruction=instruction
            )
        )

        tm.sleep((60/14)) # wait to ensure not breaking the 15 per minute limit
        parsed_data = extract_json_from_text(response.candidates[0].content.parts[0].text)  #Extract and parse JSON properly
        if parsed_data:
            results[quarter] = parsed_data
        else:
            print(f"Warning: AI output for {quarter} was not valid JSON.")
    return results

#Converts AI summary into a Pandas DataFrame and ensures chronological sorting."""
def format_as_dataframe(summary_data):
    
    def parse_quarter(q):  # Convert quarters into tuples (year, quarter_number) for proper sorting
        match = re.match(r"Q(\d) (\d{4})", q)
        if match:
            quarter, year = match.groups()
            return (int(year), int(quarter))  # (Year, Quarter as int)
        return (9999, 9999)  # If malformed, send to end

    sorted_quarters = sorted(summary_data.keys(), key=parse_quarter)  # Sort the quarters by (Year, Quarter)
    data = {
        "Top Positive Themes": [],
        "Top Negative Themes": [],
        "Future Sentiment Score": [],
        "Future Sentiment Comment": [],
        "Present Sentiment Score": [],
        "Present Sentiment Comment": [],
        "Analysts Sentiment Score": [],
        "Analysts Sentiment Comment": []
    }
    for quarter in sorted_quarters:     # Create the data frame based on Gemini's outputs.
        entry = summary_data.get(quarter, {})
        data["Top Positive Themes"].append("\n".join([f"{i+1}. {theme}" for i, theme in enumerate(entry.get("top_positive_themes", []))]))
        data["Top Negative Themes"].append("\n".join([f"{i+1}. {theme}" for i, theme in enumerate(entry.get("top_negative_themes", []))]))
        data["Future Sentiment Score"].append(entry.get("future_sentiment_score", "N/A"))
        data["Future Sentiment Comment"].append(entry.get("future_sentiment_comment", "N/A"))
        data["Present Sentiment Score"].append(entry.get("present_sentiment_score", "N/A"))
        data["Present Sentiment Comment"].append(entry.get("present_sentiment_comment", "N/A"))
        data["Analysts Sentiment Score"].append(entry.get("analysts_sentiment_score", "N/A"))
        data["Analysts Sentiment Comment"].append(entry.get("analysts_sentiment_comment", "N/A"))
    df = pd.DataFrame(data, index=sorted_quarters)
    return df

# Main function to run 
def main():
    folder = "dassault_transcripts"
    quarterly_transcripts = extract_text_from_folder(folder)

    if not quarterly_transcripts:
        print("No transcripts found or filenames do not match expected format.")
        return

    summary = summarise(quarterly_transcripts)

    summary_df = format_as_dataframe(summary)
    tools.display_dataframe_to_user(name="Quarterly Summary", dataframe=summary_df)
    summary_df.to_csv("transcript_sentiment_table_v1.csv")

# Run the main function
if __name__ == "__main__":
    main()
