# langchain.py

from pydantic import BaseModel, RootModel
from typing import List, Union, Optional
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from decouple import config
import json

# --- Your Pydantic Models (These are well-defined, no changes needed) ---
class KPIs(BaseModel):
    calories_per_100g: int
    protein: Union[str, int]
    sodium: Optional[Union[str, int]] = "0"

class Sustainability(BaseModel):
    co2_impact: Optional[str] = "low"

class Items(BaseModel):
    item_name: str
    quantity: str
    estimated_price_inr: int
    kpis: KPIs
    sustainability: Sustainability

class ClassList(RootModel[List[Items]]):
    pass


def clean_llm_output(raw_output: str) -> str:
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned


def func(data: str):
    gem_ai = config('GEM_API_KEY')
    llm = ChatGoogleGenerativeAI(google_api_key=gem_ai, model="gemini-1.5-flash", temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=ClassList)

    
    template_string = """You are a smart grocery assistant. Given a user's natural language request, return ONLY a valid JSON array with one object per item. Do NOT include any explanations, markdown, or extra text outside the JSON array. Start with [ and end with ].

    {format_instructions}

    User's Request:
    {asked_dish}
    """
    
    prompt = ChatPromptTemplate.from_template(
        template=template_string,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm

    try:
        response = chain.invoke({"asked_dish": data})
        raw_output = response.content
        print("Raw LLM Output:", raw_output)  

        cleaned_output = clean_llm_output(raw_output)
        print("Cleaned Output:", cleaned_output) 

        
        parsed_output = parser.parse(cleaned_output)
        return parsed_output.root

    except Exception as e:
        print(f"An error occurred during LLM processing or parsing: {e}")
        
        return []