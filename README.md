# select-text
A project built using FastAPI for CRUD operations on text records

## Setup
- Use `docker-compose up -d` to up the containers in detached mode

## Endpoints

- GET /records - fetches all the records
- POST /records - creates a record
- PUT /records/{record_id} - updates the record with record_id
- DELETE /records/{record_id} - deletes the record with record_id
- DELETE /records/{record_id}/{chunk_id} - deletes the selected text chunk with given chunk_id and record_id
