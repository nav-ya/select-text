from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel, Field
from pymongo import MongoClient
import os

DB = "temp_projects"
RECORDS_COLLECTION = "records"
SELECTED_CHUNKS_COLLECTION = "selected_chunks"

app = FastAPI()
client = MongoClient(os.environ.get('MONGODB_URL'))

# Models
class SelectedChunk(BaseModel):
    id: str
    record_id: str
    start: int
    end: int
    chunk_text: str

class RecordSchema(BaseModel):
    record_id: str
    record: str
    selected_chunks: List[SelectedChunk]

# Check
@app.get("/")
def read_root():
    return {"Hello": "World"}

'''
@params - None
Fetches all the records stored in collections
'''
@app.get("/records/")
async def getRecords():
    recordsCollection = client[DB][RECORDS_COLLECTION]
    records = recordsCollection.aggregate([
        {
            '$lookup': {
                'from': SELECTED_CHUNKS_COLLECTION,
                'localField': "record_id",
                'foreignField': "record_id",
                'as': "selected_chunks",
            }
        },
        { 
            '$project' : {
                '_id': 0
            }
        }
    ])

    allRecords = []
    for record in records:
        print(record)
        singleRecord = {}
        singleRecord['record_id'] = record['record_id']
        singleRecord['record'] = record['record']
        singleRecord['selected_chunks'] = []
        for chunk in record['selected_chunks']:
            del chunk['_id']
            singleRecord['selected_chunks'].append(chunk)
        allRecords.append(singleRecord)
        
    return list(allRecords)

'''
@params - RecordSchema record
Creates a new record from params passed through request body
'''
@app.post("/records/")
async def postRecord(record: RecordSchema):
    recordsCollection = client[DB][RECORDS_COLLECTION]
    selectedChunksCollection = client[DB][SELECTED_CHUNKS_COLLECTION]

    r = record.dict()
    recordName = { 'record_id': r['record_id'], 'record': r['record'] }
    recordsCollection.insert_one(recordName)

    for chunk in r['selected_chunks']:
        selectedChunksCollection.insert_one(chunk)

    return {"message": "record added"}

'''
@params - str record_id
Takes record_id as input and updates the record associated with that id
'''
@app.put("/records/{record_id}")
async def updateRecord(record_id: str, record: RecordSchema):
    recordsCollection = client[DB][RECORDS_COLLECTION]
    selectedChunksCollection = client[DB][SELECTED_CHUNKS_COLLECTION]

    record = record.dict()

    recordId = { "record_id": record_id }
    updatedRecord = { "$set" : { 'record': record['record'] } }
    recordsCollection.update_one(recordId, updatedRecord)

    for chunk in record['selected_chunks']:
        query = { "$and" : [{"id": chunk["id"]}, {"record_id": chunk["record_id"]}] }
        updatedChunk = { "$set" : { 'record_id': chunk['record_id'], 'start': chunk['start'], 'end': chunk['end'], 'chunk_text': chunk['chunk_text'] } }
        selectedChunksCollection.update_one(query, updatedChunk, True)

    return {"message": "record updated"}

'''
@params - str record_id
Takes record_id as input and deletes all the records associated with that id
'''
@app.delete("/records/{record_id}")
async def deleteRecord(record_id: str):
    recordsCollection = client[DB][RECORDS_COLLECTION]
    selectedChunksCollection = client[DB][SELECTED_CHUNKS_COLLECTION]

    recordId = { "record_id": record_id }
    recordsCollection.delete_one(recordId)
    selectedChunksCollection.delete_many(recordId)

    return {"message": "record deleted"}