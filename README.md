# Team Ideas Evaluator

A collaborative tool that evaluates product ideas from a Word document using multiple LLMs (Large Language Models) through the LangChain framework. It generates detailed and summary rating tables for each idea.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Easy Method (Recommended)](#easy-method-recommended)
  - [Manual Method](#manual-method)
  - [Testing Document Parsing Only](#testing-document-parsing-only)
- [Document Format](#document-format)
- [LLM Support](#llm-support)
- [Evaluation Dimensions](#evaluation-dimensions)
- [Output Format](#output-format)
- [Version Control](#version-control)
- [Contributing](#contributing)
- [License](#license)

## Features

- Parses product ideas from a Word document
- Evaluates each idea using multiple LLMs (both premium and free models)
- Scores ideas on dimensions like Novelty, Technical Complexity, Impact Potential, and Market Viability
- Generates detailed and summary rating tables
- Exports results as Excel files
- Provides easy-to-use scripts for both Windows and Unix/Linux/Mac

## Requirements

- Python 3.8 or higher
- API keys for LLM services (optional, but recommended for better results)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Copy `.env.template` to `.env` (important: the file must be renamed to `.env`)
   ```
   # On Windows
   copy .env.template .env
   
   # On Unix/Linux/Mac
   cp .env.template .env
   ```
   - Open the newly created `.env` file and replace the placeholder values with your actual API keys
   - This approach keeps your private API keys secure by ensuring they're not committed to Git
   - Note: The `.env` file is listed in `.gitignore` and won't be tracked by version control

## Usage

### Easy Method (Recommended)

1. Place your Word document with product ideas in the `Team_ideas_rating` folder (or use the existing `team_ideas.docx`).

2. Run the appropriate script for your operating system:
   - **Windows**:
     - Double-click on `run_evaluator.bat`
     - This script will:
       - Check if Python is installed
       - Install required packages using pip
       - Create a `.env` file from the template if it doesn't exist
       - Run the idea evaluator script
     - If you encounter permission issues, try running the script as administrator

   - **Unix/Linux/Mac**:
     - Open a terminal in the project directory
     - Make the script executable: `chmod +x run_evaluator.sh`
     - Run the script: `./run_evaluator.sh`
     - This script will:
       - Check if Python 3 is installed
       - Install required packages using pip
       - Create a `.env` file from the template if it doesn't exist
       - Run the idea evaluator script
     - If you encounter permission issues, try running with sudo: `sudo ./run_evaluator.sh`

3. Check the results in the `Team_ideas_rating` folder:
   - `detailed_ratings.xlsx`: Contains detailed ratings from each LLM for each idea
   - `summary_ratings.xlsx`: Contains summary ratings for each idea, sorted by average rating

#### Troubleshooting Helper Scripts

- **Python not found**: Ensure Python is installed and added to your PATH
- **Package installation fails**: Try running `pip install -r requirements.txt` manually
- **API keys not working**: Edit the `.env` file and ensure your API keys are valid
- **Script hangs**: The LLM API might be experiencing high traffic; try again later
- **Excel files not generated**: Check if you have write permissions in the `Team_ideas_rating` folder

### Manual Method

1. Place your Word document with product ideas in the `Team_ideas_rating` folder (or use the existing `team_ideas.docx`).

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Copy `.env.template` to `.env` (important: the file must be renamed to `.env`)
   ```
   # On Windows
   copy .env.template .env
   
   # On Unix/Linux/Mac
   cp .env.template .env
   ```
   - Open the newly created `.env` file and replace the placeholder values with your actual API keys
   - This approach keeps your private API keys secure by ensuring they're not committed to Git

4. Run the script:
   ```
   python Team_ideas_rating/idea_evaluator.py
   ```

5. Check the results in the `Team_ideas_rating` folder:
   - `detailed_ratings.xlsx`: Contains detailed ratings from each LLM for each idea
   - `summary_ratings.xlsx`: Contains summary ratings for each idea, sorted by average rating

### Testing Document Parsing Only

To test just the document parsing functionality without running the full evaluation:

```
python Team_ideas_rating/test_parser.py
```

This will extract the ideas from the document and display them without requiring any API keys.

## Document Format

The Word document should contain product ideas with identifiers:
- E1: Submitted by Enki
- G1: Submitted by Guli
- S1, S2, S3: Submitted by Shashank

Each idea should be clearly marked with its identifier (e.g., "Idea ID: E1") and include a "Project Title:" section.

## LLM Support

The script supports the following LLMs:

### Premium Models (API keys required)
- OpenAI GPT (e.g., gpt-4o)
- Groq with LLaMA 3 (70B)
- Google Gemini 1.5 Flash
- Perplexity.ai with Sonar model

### Testing Mode
If no API keys are provided, the script will use mock LLMs for testing purposes.

## Evaluation Dimensions

Each idea is evaluated on the following dimensions:

1. Novelty - How original or unique is the idea?
2. Technical Complexity - How challenging is it to implement?
3. Impact Potential - What's the potential benefit or social relevance?
4. Market Viability - How likely is it to succeed commercially?
5. Feasibility - Is it practical to build in the near term?
6. User Desirability - Will users genuinely want or need it?
7. Trend Alignment - Does it align with emerging trends?

## Output Format

### Detailed Ratings Table
- Columns: Idea ID, Idea Title, LLM, Dimension, Score, Remark
- Contains individual ratings from each LLM for each dimension of each idea

### Summary Table
- Columns: Idea ID, Idea Title, [Dimension Scores], Average Rating
- Contains average ratings across all LLMs for each dimension
- All ratings are rounded to 1 decimal place for better readability
- Sorted in descending order of average rating

## Version Control

This project uses Git for version control. A `.gitignore` file is included to exclude:
- Environment files (.env)
- Virtual environment directories
- Generated output files (Excel files)
- Python cache files
- IDE-specific files

> **Important Note**: The `.env` file is intentionally excluded from version control for security reasons, as it contains your private API keys. However, the `.env.template` file IS tracked by Git, allowing you to easily share the project structure without exposing sensitive information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.