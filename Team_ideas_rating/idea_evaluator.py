"""
Idea Evaluator Script

This script reads product ideas from a Word document, evaluates them using multiple LLMs,
and generates detailed and summary rating tables.
"""

import os
import docx
import pandas as pd
from typing import List, Dict, Any, Tuple
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.llms.base import LLM
import requests
from typing import Optional, List, Mapping, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
import json
import re
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient
import textwrap
from colorama import init

# Initialize colorama
init()

class PerplexityLLM(LLM):
    """LLM wrapper for Perplexity.ai API using OpenAI client."""
    
    api_key: str
    model_name: str = "sonar"
    temperature: float = 0.7
    max_tokens: int = 500
    
    @property
    def _llm_type(self) -> str:
        return "perplexity"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Perplexity API using OpenAI client and return the response."""
        client = OpenAIClient(api_key=self.api_key, base_url="https://api.perplexity.ai")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

# Load environment variables from .env file
load_dotenv()

# Print a message about API keys
print("Checking for API keys...")
api_keys = {
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
    "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    "PERPLEXITY_API_KEY": os.environ.get("PERPLEXITY_API_KEY")
}

available_keys = [key for key, value in api_keys.items() if value]
if available_keys:
    print(f"Found API keys for: {', '.join(available_keys)}")
else:
    print("Warning: No API keys found. Using mock LLMs for testing.")
    print("To use real LLMs, copy .env.template to .env and add your API keys.")

# Define paths
DOCUMENT_PATH = os.path.join("Team_ideas_rating", "team_ideas.docx")
OUTPUT_DETAILED_PATH = os.path.join("Team_ideas_rating", "detailed_ratings.xlsx")
OUTPUT_SUMMARY_PATH = os.path.join("Team_ideas_rating", "summary_ratings.xlsx")

class Idea:
    """Class to represent a product idea."""
    
    def __init__(self, id: str, title: str, description: str):
        self.id = id
        self.title = title
        self.description = description
    
    def __str__(self):
        return f"{self.id}: {self.title}\n{self.description}"

def extract_ideas_from_doc(doc_path: str) -> List[Idea]:
    """
    Extract ideas from the Word document.
    
    Args:
        doc_path: Path to the Word document
        
    Returns:
        List of Idea objects
    """
    print(f"Reading document: {doc_path}")
    doc = docx.Document(doc_path)
    
    # Extract text from the document
    full_text = "\n".join([para.text for para in doc.paragraphs])
    
    # Define patterns to identify ideas
    idea_patterns = {
        "E1": r"Idea ID: E1.*?(?=Idea ID: G1|Idea ID: S1|$)",
        "G1": r"Idea ID: G1.*?(?=Idea ID: E1|Idea ID: S1|$)",
        "S1": r"Idea ID: S1.*?(?=Idea ID: E1|Idea ID: G1|Idea ID: S2|$)",
        "S2": r"Idea ID: S2.*?(?=Idea ID: E1|Idea ID: G1|Idea ID: S1|Idea ID: S3|$)",
        "S3": r"Idea ID: S3.*?(?=Idea ID: E1|Idea ID: G1|Idea ID: S1|Idea ID: S2|$)"
    }
    
    ideas = []
    
    for idea_id, pattern in idea_patterns.items():
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            idea_text = match.group(0).strip()
            # Extract title (assuming it's the line after "Project Title:")
            title_match = re.search(r"Project Title:(.*?)(?:\n|$)", idea_text)
            title = title_match.group(1).strip() if title_match else "Untitled"
            
            # Extract description (everything after the title)
            description = idea_text[title_match.end():].strip() if title_match else idea_text
            
            ideas.append(Idea(idea_id, title, description))
    
    print(f"Extracted {len(ideas)} ideas from the document")
    return ideas

def setup_llms() -> Dict[str, Any]:
    """
    Set up connections to multiple LLMs.
    
    Returns:
        Dictionary of LLM instances
    """
    llms = {}
    
    # Set up OpenAI models
    if os.environ.get("OPENAI_API_KEY"):
        llms["GPT-4"] = ChatOpenAI(model_name="gpt-4o", temperature=0.2)
    
    # Set up Groq models
    if os.environ.get("GROQ_API_KEY"):
        llms["LLaMA-3-70B"] = ChatGroq(model="llama3-70b-8192", temperature=0.2)
    
    # Set up Google models
    if os.environ.get("GOOGLE_API_KEY"):
        llms["Gemini-1.5-Flash"] = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    
    # Set up Perplexity models
    if os.environ.get("PERPLEXITY_API_KEY"):
        # Print Perplexity API key (masked for security)
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        print(f"Perplexity API Key: {perplexity_api_key[:7]}.....{perplexity_api_key[-7:]}")
        
        llms["Perplexity-Sonar"] = PerplexityLLM(
            api_key=perplexity_api_key,
            model_name="sonar",
            temperature=0.7,
            max_tokens=500
        )
    
    # If no API keys are set, use a mock LLM for testing
    if not llms:
        print("Warning: No API keys found. Using mock LLMs for testing.")
        from langchain.llms.fake import FakeListLLM
        
        llms["Mock-LLM-1"] = FakeListLLM(responses=["This is a mock response from LLM 1"])
        llms["Mock-LLM-2"] = FakeListLLM(responses=["This is a mock response from LLM 2"])
        llms["Mock-LLM-3"] = FakeListLLM(responses=["This is a mock response from LLM 3"])
        llms["Mock-LLM-4"] = FakeListLLM(responses=["This is a mock response from LLM 4"])
    
    print(f"Set up {len(llms)} LLM connections")
    return llms

def create_evaluation_prompt() -> PromptTemplate:
    """
    Create a prompt template for idea evaluation.
    
    Returns:
        PromptTemplate instance
    """
    template = """
    You are an expert product evaluator. Please evaluate the following product idea:
    
    IDEA ID: {idea_id}
    TITLE: {idea_title}
    DESCRIPTION: {idea_description}
    
    Rate this idea on a scale of 1 to 10 (where 10 is the highest) across the following dimensions:
    
    1. Novelty - How original or unique is the idea?
    2. Technical Complexity - How challenging is it to implement?
    3. Impact Potential - What's the potential benefit or social relevance?
    4. Market Viability - How likely is it to succeed commercially?
    5. Feasibility - Is it practical to build in the near term?
    6. User Desirability - Will users genuinely want or need it?
    7. Trend Alignment - Does it align with emerging trends?
    
    For each dimension, provide:
    1. A numerical rating (1-10)
    2. A brief remark (1-3 lines) explaining your rating
    
    Format your response as a JSON object with the following structure:
    {{
        "novelty": {{"score": <1-10>, "remark": "<your remark>"}},
        "technical_complexity": {{"score": <1-10>, "remark": "<your remark>"}},
        "impact_potential": {{"score": <1-10>, "remark": "<your remark>"}},
        "market_viability": {{"score": <1-10>, "remark": "<your remark>"}},
        "feasibility": {{"score": <1-10>, "remark": "<your remark>"}},
        "user_desirability": {{"score": <1-10>, "remark": "<your remark>"}},
        "trend_alignment": {{"score": <1-10>, "remark": "<your remark>"}},
        "overall_impression": "<1-2 sentence summary of your overall impression>"
    }}
    
    Ensure your response is valid JSON with no additional text before or after.
    """
    
    return PromptTemplate(
        input_variables=["idea_id", "idea_title", "idea_description"],
        template=template
    )

def evaluate_idea(idea: Idea, llms: Dict[str, Any], prompt_template: PromptTemplate) -> Dict[str, Any]:
    """
    Evaluate an idea using multiple LLMs.
    
    Args:
        idea: Idea object
        llms: Dictionary of LLM instances
        prompt_template: PromptTemplate instance
        
    Returns:
        Dictionary of evaluation results
    """
    print(f"Evaluating idea {idea.id}: {idea.title}")
    print(f"Number of LLMs available: {len(llms)}")
    print(f"LLM names: {', '.join(llms.keys())}")
    
    results = {}
    
    for llm_name, llm in llms.items():
        print(f"\n  Using {llm_name}...")
        
        try:
            # Create a chain for this LLM
            chain = LLMChain(llm=llm, prompt=prompt_template)
            
            # Run the chain
            print(f"  Sending request to {llm_name}...")
            response = chain.run(
                idea_id=idea.id,
                idea_title=idea.title,
                idea_description=idea.description
            )
            print(f"  Received response from {llm_name}")
            
            # Parse the JSON response
            try:
                print(f"  Parsing JSON response from {llm_name}...")
                
                # Clean up the response to extract just the JSON part
                cleaned_response = response
                
                # Try to find JSON object between curly braces
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)
                    print(f"  Extracted JSON object from response")
                
                # Try to parse the JSON
                evaluation = json.loads(cleaned_response)
                
                # Verify that the evaluation contains the expected dimensions
                expected_dimensions = ["novelty", "technical_complexity", "impact_potential", 
                                      "market_viability", "feasibility", "user_desirability", 
                                      "trend_alignment"]
                
                missing_dimensions = [dim for dim in expected_dimensions if dim not in evaluation]
                if missing_dimensions:
                    print(f"  Warning: Missing dimensions in {llm_name} evaluation: {missing_dimensions}")
                    # Try to extract missing dimensions from the response if possible
                    for dim in missing_dimensions:
                        dim_pattern = rf'"{dim}".*?"score".*?(\d+)'
                        score_match = re.search(dim_pattern, response, re.IGNORECASE | re.DOTALL)
                        if score_match:
                            score = int(score_match.group(1))
                            remark_pattern = rf'"{dim}".*?"remark".*?"([^"]+)"'
                            remark_match = re.search(remark_pattern, response, re.IGNORECASE | re.DOTALL)
                            remark = remark_match.group(1) if remark_match else "No remark provided"
                            evaluation[dim] = {"score": score, "remark": remark}
                            print(f"  Extracted {dim} from response text: score={score}")
                
                results[llm_name] = evaluation
                print(f"  {llm_name} evaluation complete - SUCCESS")
                print(f"  Dimensions found: {list(evaluation.keys())}")
            except json.JSONDecodeError:
                print(f"  Error: {llm_name} did not return valid JSON.")
                print(f"  Response preview: {response[:100]}...")
                
                # Attempt to extract structured data from non-JSON response
                try:
                    print(f"  Attempting to extract structured data from non-JSON response...")
                    extracted_data = {}
                    
                    # Extract dimensions using regex patterns
                    for dim in ["novelty", "technical_complexity", "impact_potential", 
                               "market_viability", "feasibility", "user_desirability", 
                               "trend_alignment"]:
                        # Look for patterns like "Novelty: 8" or "Novelty - 8"
                        score_pattern = rf'{dim}[:\s-]+(\d+)(?:/10)?'
                        score_match = re.search(score_pattern, response, re.IGNORECASE)
                        
                        if score_match:
                            score = int(score_match.group(1))
                            
                            # Try to find a remark for this dimension
                            remark_pattern = rf'{dim}[:\s-]+\d+(?:/10)?[:\s-]*(.*?)(?=\n\n|\n[A-Z]|$)'
                            remark_match = re.search(remark_pattern, response, re.IGNORECASE | re.DOTALL)
                            remark = remark_match.group(1).strip() if remark_match else "No remark provided"
                            
                            extracted_data[dim] = {"score": score, "remark": remark}
                            print(f"  Extracted {dim} from text: score={score}")
                    
                    if extracted_data:
                        print(f"  Successfully extracted data for {len(extracted_data)} dimensions")
                        results[llm_name] = extracted_data
                    else:
                        raise ValueError("Could not extract structured data")
                        
                except Exception as e:
                    print(f"  Failed to extract structured data: {str(e)}")
                    results[llm_name] = {
                        "error": "Failed to parse JSON response",
                        "raw_response": response
                    }
        except Exception as e:
            print(f"  Error with {llm_name}: {str(e)}")
            results[llm_name] = {
                "error": str(e)
            }
    
    # Print summary of results
    successful_llms = [name for name, eval in results.items() if "error" not in eval]
    failed_llms = [name for name, eval in results.items() if "error" in eval]
    
    print(f"\nEvaluation summary for idea {idea.id}:")
    print(f"  Successful evaluations: {len(successful_llms)} ({', '.join(successful_llms)})")
    print(f"  Failed evaluations: {len(failed_llms)} ({', '.join(failed_llms)})")
    
    return results

def generate_tables(all_evaluations: Dict[str, Dict[str, Any]], ideas: List[Idea]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate detailed and summary tables from evaluation results.
    
    Args:
        all_evaluations: Dictionary of evaluation results for all ideas
        ideas: List of Idea objects
        
    Returns:
        Tuple of (detailed_df, summary_df)
    """
    print("Generating tables...")
    
    # Create detailed ratings dataframe
    detailed_rows = []
    
    for idea in ideas:
        idea_evaluations = all_evaluations.get(idea.id, {})
        
        for llm_name, evaluation in idea_evaluations.items():
            if "error" in evaluation:
                continue
                
            for dimension in ["novelty", "technical_complexity", "impact_potential", "market_viability", 
                             "feasibility", "user_desirability", "trend_alignment"]:
                if dimension in evaluation:
                    detailed_rows.append({
                        "Idea ID": idea.id,
                        "Idea Title": idea.title,
                        "LLM": llm_name,
                        "Dimension": dimension.replace("_", " ").title(),
                        "Score": evaluation[dimension]["score"],
                        "Remark": evaluation[dimension]["remark"]
                    })
    
    detailed_df = pd.DataFrame(detailed_rows)
    
    # Create summary ratings dataframe
    summary_rows = []
    
    for idea in ideas:
        idea_evaluations = all_evaluations.get(idea.id, {})
        dimension_scores = {
            "novelty": [],
            "technical_complexity": [],
            "impact_potential": [],
            "market_viability": [],
            "feasibility": [],
            "user_desirability": [],
            "trend_alignment": []
        }
        
        for llm_name, evaluation in idea_evaluations.items():
            if "error" in evaluation:
                continue
                
            for dimension in dimension_scores.keys():
                if dimension in evaluation:
                    dimension_scores[dimension].append(evaluation[dimension]["score"])
        
        # Calculate average scores and round to 1 decimal place
        avg_scores = {dim: round(sum(scores)/len(scores), 1) if scores else 0.0 
                     for dim, scores in dimension_scores.items()}
        
        # Calculate overall average and round to 1 decimal place
        overall_avg = round(sum(avg_scores.values()) / len(avg_scores), 1) if avg_scores else 0.0
        
        summary_rows.append({
            "Idea ID": idea.id,
            "Idea Title": idea.title,
            "Novelty": avg_scores["novelty"],
            "Technical Complexity": avg_scores["technical_complexity"],
            "Impact Potential": avg_scores["impact_potential"],
            "Market Viability": avg_scores["market_viability"],
            "Feasibility": avg_scores["feasibility"],
            "User Desirability": avg_scores["user_desirability"],
            "Trend Alignment": avg_scores["trend_alignment"],
            "Average Rating": overall_avg
        })
    
    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values(by="Average Rating", ascending=False)
    
    print("Tables generated")
    return detailed_df, summary_df

def export_tables(detailed_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    """
    Export tables to Excel files.
    
    Args:
        detailed_df: Detailed ratings dataframe
        summary_df: Summary ratings dataframe
    """
    print(f"Exporting detailed ratings to {OUTPUT_DETAILED_PATH}")
    detailed_df.to_excel(OUTPUT_DETAILED_PATH, index=False)
    
    # Round all numeric columns in summary_df to 1 decimal place for display
    numeric_columns = ['Novelty', 'Technical Complexity', 'Impact Potential', 
                      'Market Viability', 'Feasibility', 'User Desirability', 
                      'Trend Alignment', 'Average Rating']
    
    for col in numeric_columns:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(1)
    
    print(f"Exporting summary ratings to {OUTPUT_SUMMARY_PATH}")
    summary_df.to_excel(OUTPUT_SUMMARY_PATH, index=False)
    
    print("Export complete")

def main():
    """Main function to run the idea evaluation process."""
    print("Starting idea evaluation process...")
    
    # Extract ideas from the document
    ideas = extract_ideas_from_doc(DOCUMENT_PATH)
    
    # Set up LLMs
    llms = setup_llms()
    
    # Create evaluation prompt
    prompt_template = create_evaluation_prompt()
    
    # Evaluate ideas
    all_evaluations = {}
    for idea in ideas:
        all_evaluations[idea.id] = evaluate_idea(idea, llms, prompt_template)
    
    # Generate tables
    detailed_df, summary_df = generate_tables(all_evaluations, ideas)
    
    # Export tables
    export_tables(detailed_df, summary_df)
    
    print("Idea evaluation process complete!")

if __name__ == "__main__":
    main()