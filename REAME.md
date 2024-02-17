Certainly! Below is a sample README for your application, outlining the steps to set up and run it:

---

# Multiple Choice Question (MCQ) Generator

This application generates multiple-choice questions (MCQs) based on the content of provided chapters. Users can select a chapter, and the application will generate a question with options and the correct answer. Additionally, users can submit their answers to check if they are correct.

## Prerequisites

Before running this application, ensure you have docker installed

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Inside frontend/.streamlit create a secrets.toml file with your firebase api key.
   
3. Create a `.env` file similar to .env.example with the credentials:

### Data Ingestion
1. Store you pdf files in the `backend/data/` directory

2. Run the following command to ingest the data:
   ```bash
   python ingest.py
   ```
   This will create a `processed_data/` directory with the processed data stored as .pkls

## Running the Application
1. Run the app using docker
   ```
   docker compose up --build
   ```
   or
   ```
   docker-compose up --build
   ```

2. Access the Swagger UI to interact with the API at `http://localhost:8000/docs`.

## Usage

### Generating an MCQ

- Send a POST request to `/generate-mcq/{chapter_index}` where `{chapter_index}` is the index of the chapter for which you want to generate an MCQ.
- The response will include the generated question, options, correct answer, and an explanation.

## Testing

You can test the application using tools like `curl`, Postman, or Python's `requests` library. You can also run 
```bash
python response.py
```





