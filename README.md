# Web Search AI Agent

A Python-based intelligent web search agent that leverages AI to provide enhanced search capabilities.

## Features

- AI-powered web search functionality
- Database integration using Chroma
- Web interface for search interactions
- Query processing and result optimization

## Project Structure

```
Web-Search-AI-Agent/
├── main.py              # Main application entry point
├── search.py            # Search functionality implementation
├── query.py            # Query processing logic
├── model.py            # AI model integration
├── create_database.py  # Database initialization
├── get_result.py      # Result processing
├── static/            # Static web files
│   └── index.html    # Web interface
├── data/             # Data storage
└── chroma/           # Chroma database files
```

## Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`
4. Initialize the database:

```bash
python create_database.py
```

## Usage

1. Start the application:

```bash
python main.py
```

2. Open your web browser and navigate to the provided URL
3. Enter your search query through the web interface

## Environment Variables

Create a `.env` file in the root directory with the following variables:

- Required environment variables will be listed here
- Refer to `.env.example` for a template

## Demo https://youtu.be/JX85doSloPg


All required packages are listed in `requirements.txt`


