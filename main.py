from copy import deepcopy, copy

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient

# db - MongoDB
# document-oriented db
# only one collection ( cats )
cluster = MongoClient(
    "mongodb+srv://stukantimur:06UmxVawhKDZaSN1@cluster0.s7w3e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

my_db = cluster["catsdb"]
collection = my_db.cats
app = FastAPI()


@app.get("/")
def test():
    return {"message": "test is done"}


@app.post("/cats/")
def create_user(cat: dict):
    if "name" not in cat or "age" not in cat:
        return JSONResponse(status_code=400, content={"message": "name and age fields are required"})

    collection.insert_one(cat)
    cat.pop("_id")
    return cat


@app.get("/cats/")
def get_cats():
    return [{**cat, "_id": str(cat["_id"])} for cat in collection.find()]


@app.get("/cats/{name}/")
def get_cat_by_name(name: str):
    cat = collection.find_one({"name": name})
    if not cat:
        return JSONResponse(status_code=404, content={"message": "not found"})
    cat.pop("_id")
    return cat


@app.get("/cat/filter/")
def get_cat_filter(name: str = None, age: int = None):
    query = {}
    if name:
        query["name"] = name
    if age:
        query["age"] = age

    cats = list(collection.aggregate([{"$match": query}]))

    return [{**cat, "_id": str(cat["_id"])} for cat in cats]


@app.get("/cat/random/")
def get_random_cat():
    cat = next(collection.aggregate([{"$sample": {"size": 1}}]))
    cat.pop("_id")
    return cat


@app.put("/cats/{name}/")
def update_cat(name: str, update_dict: dict):
    updated_cat = collection.update_one({"name": name}, {"$set": update_dict})
    if updated_cat.matched_count == 0:
        return JSONResponse(status_code=404, content={"message": "not found"})

    return JSONResponse(status_code=200, content={"message": "updated successfully"})


@app.delete("/cats/{name}/")
def delete_cat(name: str):
    cat = collection.delete_one({"name": name})
    if cat.deleted_count == 1:
        return JSONResponse(status_code=200, content={"message": "successfully deleted"})
    return JSONResponse(status_code=404, content={"message": "not found"})
