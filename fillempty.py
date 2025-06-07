# -*- coding: utf-8 -*-
'''
Fill the empty stock_code field in the extracted stock data from YouTube transcripts.
YouTube Stock Opinion Extractor
'''



import os
from string import Template
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)  

def get_company_code(company_list, llm_model="gpt-4.1-mini"):
    '''
    '''
    # validate llm_model
    valid_models = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o","o4-mini"]#, "gpt-4", "gpt-3.5-turbo"]
    if llm_model not in valid_models:
        raise ValueError(f"Invalid model name: {llm_model}. Choose from {valid_models}.")

    system_prompt = "You are a financial analyst reviewing a YouTube transcript."
    template = Template("""
        Please find the stock tickers for the following companies:
        $list
        
        Return in JSON:
        [ { "company": ..., "ticker": ..., "exchange": ... } ]
        """) 
    company_list =company_list[:20]
    stock_list = "\n".join(f"- {c}" for c in company_list)
    user_prompt = template.substitute(list=stock_list)

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
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    import json
    model = "gpt-4.1-mini"  # Change to your preferred model rank #1
    #model = "gpt-4o-mini"  # Change to your preferred model rank #2
    #model = "gpt-4o"  # Change to your preferred model rank unknown
    #model = "o4-mini"  # Change to your preferred model , rank #3
    with open("output/extracted_missing_stock_codes.json", "r", encoding="utf-8") as f:
        company_list = json.load(f)
    # splite company_list into chunks of 20
    company_ll = [company_list[i:i + 20] for i in range(0, len(company_list), 20)]

    result = []
    for idx, company_list in enumerate(company_ll):
        output = get_company_code(company_list, llm_model=model)
        output2 = output.replace("```json", "").replace("```", "").strip()
        try:
            output_obj = json.loads(output2)
        except Exception as e:
            print(f"Error decoding JSON for chunk {idx + 1}: {e}")
            print(f"Output: {output2}")
            continue
        # check the N/A
        result.extend(output_obj)
        print(f"Processed chunk {idx + 1}/{len(company_ll)}: {len(company_list)} companies")
        
    with open("output/stock_codes.json", "w", encoding="utf-8") as f:
        json.dump(result, f)

