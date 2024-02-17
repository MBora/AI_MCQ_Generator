import os
import openai
from openai import OpenAI
import pickle

import llama_index.llms

# load OPENAI_API_KEY from .env file
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from openai import OpenAI
client = OpenAI()

from llama_index.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
    EntityExtractor,
    BaseExtractor,
)
from llama_index.ingestion import IngestionPipeline
from llama_index import SimpleDirectoryReader
from llama_index.text_splitter import SentenceSplitter, TokenTextSplitter
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.schema import MetadataMode
text_splitter = SentenceSplitter(
    separator=" ", chunk_size=2048, chunk_overlap=512
)
ingestion_llm = llama_index.llms.Gemini(temperature=0.4, model="models/gemini-pro", max_tokens=2048)
extractors = [
    TitleExtractor(nodes=5, llm=ingestion_llm),
    # QuestionsAnsweredExtractor(questions=6, llm=ingestion_llm),
    # EntityExtractor(prediction_threshold=0.5),
    # SummaryExtractor(summaries=["prev", "self"], llm=llm),
    KeywordExtractor(keywords=20, llm=ingestion_llm),
]
# transformations = [text_splitter] + extractors
transformations = [text_splitter]

# Directory paths
input_folder = "./data"
output_folder = "./processed_data"
log_file = "./processed_data/log.txt"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Read the log file to find out which files have been processed
processed_files = set()
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        processed_files = set(f.read().splitlines())

# Process each file in the input folder
for file_name in os.listdir(input_folder):
    file_path = os.path.join(input_folder, file_name)
    if os.path.isfile(file_path) and file_name not in processed_files:
        print(f"Processing {file_name}...")
        try:
            # Ingest document
            docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
            pipeline = IngestionPipeline(transformations=transformations)
            nodes = pipeline.run(documents=docs)

            # Create output file name
            base_file_name = os.path.splitext(file_name)[0]
            output_file_name = f"{base_file_name}_nodes.pkl"
            output_file_path = os.path.join(output_folder, output_file_name)

            # Store nodes in a pickle file
            with open(output_file_path, "wb") as f:
                pickle.dump(nodes, f)

            # Update log file
            with open(log_file, "a") as log:
                log.write(file_name + "\n")

            print(f"Nodes from {file_name} saved to {output_file_path}")
            # print(nodes[0].get_content(metadata_mode=MetadataMode.LLM))
            # input("Press Enter to continue...")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

# docs = SimpleDirectoryReader(input_files=["./data/Chap2 - UE3 - Hemato_en.pdf"]).load_data()
# pipeline = IngestionPipeline(transformations=transformations)
# nodes = pipeline.run(documents=docs)
# print(nodes[1].get_content(metadata_mode=MetadataMode.LLM))
# # store nodes as pkl
# import pickle
# with open("nodes.pkl", "wb") as f:
#     pickle.dump(nodes, f)
    
