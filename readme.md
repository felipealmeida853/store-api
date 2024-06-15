# Document Storage API

This is a simple API to store, retrieve, and delete any type of documents in a bucket. The API uses FastAPI for handling HTTP requests and boto3 for interacting with an object store that uses the S3 interface.

## Features

- **Upload documents**: Store any type of document in the bucket.
- **Retrieve documents**: Get documents from the bucket using their unique identifiers.
- **Delete documents**: Remove documents from the bucket.

## Requirements

- Python 3.10+
- FastAPI
- boto3
- An S3-compatible object store

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/felipealmeida853/store-api.git
    cd store-api
    ```

2. **Create a virtual environment and activate it**:

    ```sh
    pyenv virtualenv 3.10.0 api
    pyenv activate api  
    ```

3. **Install the dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

Before running the API, you need to configure your S3-compatible object store credentials. You can do this by setting environment variables or by using a configuration file.

### Environment Variables

Set the following environment variables in `.env` with your S3-compatible object store credentials:

- `BUCKET_SERVICE_NAME`
- `BUCKET_REGION`
- `BUCKET_ACCESS_KEY_ID`
- `BUCKET_SECRET_ACCESS_KEY`
- `BUCKET_ENDPOINT_URL` (if applicable)

## Usage

1.  **Run the dependencies (MongoDB)**:

    ```sh
        docker compose up -d
    ```

2. **Run the FastAPI server**:

    ```sh
        uvicorn app.main:app --reload
        or make run
    ```

## About Endpoints

To discover how to use you can access `http://localhost:8000/docs`
