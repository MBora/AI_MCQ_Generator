Certainly! Below is a sample README for your application, outlining the steps to set up and run it:

---

# Multiple Choice Question (MCQ) Generator

This application generates multiple-choice questions (MCQs) based on the content of provided chapters. Users can select a chapter, and the application will generate a question with options and the correct answer. Additionally, users can submit their answers to check if they are correct.

## Prerequisites

Before running this application, ensure you have the following installed:
- Python 3.10
- FastAPI
- Uvicorn
- OpenAI Python library
- python-dotenv library
- requests library (for testing)
- llama-index library

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the application directory:
   ```bash
   cd src
   ```

3. Install the required Python libraries:
   ```bash
   pip install fastapi uvicorn openai python-dotenv requests llama-index
   ```

4. Create a `.env` file in the src directory of the application and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Data Ingestion
1. Store you pdf files in the `data/` directory

2. Run the following command to ingest the data:
   ```bash
   python ingest.py
   ```
   This will create a `processed_data/` directory with the processed data stored as .pkls
## Running the Application
1. Create the mysql database using docker
   ```
   docker pull mysql
   
   docker run --name mysql-db -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=mydatabase -p 3306:3306 -d mysql
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The `--reload` flag enables auto-reloading of the server on code changes.

3. Access the Swagger UI to interact with the API at `http://localhost:8000/docs`.

## Usage

### Generating an MCQ

- Send a POST request to `/generate-mcq/{chapter_index}` where `{chapter_index}` is the index of the chapter for which you want to generate an MCQ.
- The response will include the generated question, options, correct answer, and an explanation.

## Testing

You can test the application using tools like `curl`, Postman, or Python's `requests` library. You can also run 
```bash
python response.py
```





