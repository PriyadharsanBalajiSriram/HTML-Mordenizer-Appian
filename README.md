# HTML-Modernizer
A smart tool using LLM agents to enhance user-generated HTML by applying modern web design best practices.

## Getting Started

Follow the steps below to set up and run the project:

### Create a venv environment

```bash
python -m venv env_name
```

### Clone the Repository

```bash
git clone https://github.com/Power108/HTML-Modernizer.git
cd html-modernizer
```

### Install Dependencies

Make sure you have Python installed. Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Create a .env file in the root directory and add the following content:

```env
GEMINI_API_KEY="your_api_key"
```

### Input HTML Files
Place your raw HTML file that needs to be modernized in a file named input.html inside the data/input directory:

```css
data/
└── input/
    └── input.html
```

### Output HTML Files
The modernized HTML files will be saved in the data/generated directory:

```css
data/
├── input/
│   └── input.html
└── generated/
    └── generated_html_1.html
```

### Run the Application
Run the application using:

```bash
python app.py
```
