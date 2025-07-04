# -*- coding: utf-8 -*-
'''
YouTube Stock Opinion Extractor 
This script extracts stock opinions from YouTube video transcripts using OpenAI's GPT-4 model.
It uses yt-dlp to download the transcript, processes it with OpenAI's API, and formats the 
output as JSON.
'''
import os
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)  
#models = client.models.list()
#for m in models.data:
#    print(m.id)

def extract_stocks_from_transcript(transcript_text, llm_model="gpt-4.1-mini"):
    '''
    Extract stock opinions from a YouTube transcript using OpenAI's GPT-4 model.
    Args:
        transcript_text (str): The cleaned transcript text from a YouTube video.
        Returns:
        str: JSON formatted string containing stock names, ticker symbols, opinions, sources, and quotes.
    '''
    # validate llm_model
    valid_models = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o","o4-mini"]#, "gpt-4", "gpt-3.5-turbo"]
    if llm_model not in valid_models:
        raise ValueError(f"Invalid model name: {llm_model}. Choose from {valid_models}.")

    system_prompt = "You are a financial analyst reviewing a YouTube transcript."
    user_prompt = f"""
        Given the following transcript, extract:
        
        1. Stock/company names mentioned
        2. Stock ticker symbols if available
        3. Host's opinion (positive / negative / neutral)
        4. Whether it's the host's own opinion or quoted from another source
        5. Include short supporting quote
        
        Format as JSON like this:
        [
          {{
            "stock": "Tesla",
            "stock_code": "TSLA",
            "opinion": "positive",
            "source": "host",
            "quote": "I think Tesla is a great long-term bet."
          }},
          ...
        ]
        
        Transcript:
        {transcript_text}
    """

    if llm_model == "o4-mini":
        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return response.choices[0].message.content
    response = client.chat.completions.create(
        #model="gpt-4o",
        # gpt-4.1-mini
        #model="gpt-4o-mini",
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def main(extract_function, model):
    """
    Main function to extract stock opinions from YouTube transcripts.
    """
    for file in os.listdir("output/cleaned"):
        if file.endswith(".txt"):
            video_id = file.split(".")[0]
            with open(f"output/cleaned/{file}", "r", encoding="utf-8") as f:
                transcript = f.read().strip()
            #video_id = "20250605"
            #with open(f"output/cleaned/{video_id}.txt", "r", encoding="utf-8") as f:
            #    transcript = f.read().strip()
            output = extract_function(transcript, llm_model=model)
            print(output)
            output = output.replace("```json", "").replace("```", "").strip()
            output_dict = json.loads(output)

            with open(f"output/extracted/{video_id}_{model}.json", "w", encoding="utf-8") as f:
                json.dump(output_dict, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    model = "gpt-4.1-mini"  #  rank #1
    #model = "gpt-4o-mini"  # rank #2
    #model = "gpt-4o"  #  rank unknown
    #model = "o4-mini"  #  rank #3
    main(extract_stocks_from_transcript, model)

