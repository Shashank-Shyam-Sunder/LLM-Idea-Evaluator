"""
Test script for the idea parser functionality.

This script tests the document parsing functionality of the idea_evaluator.py script
without requiring API keys for LLMs.
"""

import os
import sys
from idea_evaluator import extract_ideas_from_doc, Idea

def main():
    """Test the idea parser functionality."""
    print("Testing idea parser functionality...")
    
    # Define the document path
    doc_path = os.path.join(os.path.dirname(__file__), "team_ideas.docx")
    
    # Check if the document exists
    if not os.path.exists(doc_path):
        print(f"Error: Document not found at {doc_path}")
        return
    
    # Extract ideas from the document
    try:
        ideas = extract_ideas_from_doc(doc_path)
        
        # Print the extracted ideas
        print(f"\nSuccessfully extracted {len(ideas)} ideas from the document:")
        for i, idea in enumerate(ideas, 1):
            print(f"\n{i}. {idea.id}: {idea.title}")
            print(f"   Description: {idea.description[:100]}...")
        
        # Verify that all expected ideas were extracted
        expected_ids = ["E1", "G1", "S1", "S2", "S3"]
        found_ids = [idea.id for idea in ideas]
        
        missing_ids = [id for id in expected_ids if id not in found_ids]
        if missing_ids:
            print(f"\nWarning: The following expected ideas were not found: {', '.join(missing_ids)}")
        else:
            print("\nAll expected ideas were successfully extracted!")
            
    except Exception as e:
        print(f"Error extracting ideas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()