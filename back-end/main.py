from fastapi import FastAPI, HTTPException
from linkedin import linkedin
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import creds

from dotenv import load_dotenv
import os


app = FastAPI()
load_dotenv()

# MongoDB connection
uri = f"mongodb+srv://{creds._MONGO_USERNAME}:{creds._MONGO_PASSWORD}@portfolio-cluster-1.uofphnn.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
client.admin.command('ping')
print("Pinged your deployment. You successfully connected to MongoDB!")
db = client["portfolio_db"]

@app.get("/")
def home():
    # Retrieve user profile data from MongoDB
    return {"message": "Welcome"}

@app.get("/api/profile/{user_id}")
def get_profile(user_id: str):
    # Retrieve user profile data from MongoDB
    profile = db.profiles.find_one({"user_id": user_id})
    if profile:
        return profile
    else:
        raise HTTPException(status_code=404, detail="Profile not found.")

@app.post("/api/profile")
def save_profile(profile_data: dict):
    # Save user profile data to MongoDB
    db.profiles.insert_one(profile_data)

    return {"message": "Profile saved successfully."}

@app.post("/api/import-linkedin-data")
def import_linkedin_data(linkedin_data: dict):
    # Process and parse LinkedIn data
    user_id = linkedin_data["user_id"]
    name = linkedin_data["name"]
    headline = linkedin_data["headline"]
    work_experience = linkedin_data["work_experience"]
    education = linkedin_data["education"]
    skills = linkedin_data["skills"]

    # Check if the user profile already exists in MongoDB
    existing_profile = db.profiles.find_one({"user_id": user_id})
    if existing_profile:
        # Update the existing profile
        db.profiles.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": name,
                "headline": headline,
                "work_experience": work_experience,
                "education": education,
                "skills": skills
            }}
        )
    else:
        # Save a new profile
        profile_data = {
            "user_id": user_id,
            "name": name,
            "headline": headline,
            "work_experience": work_experience,
            "education": education,
            "skills": skills
        }
        db.profiles.insert_one(profile_data)

    return {"message": "LinkedIn data imported successfully."}


def save_profile(parsed_data: dict):
    # Save or update the user's profile in MongoDB
    user_id = parsed_data["user_id"]

    # Check if the user profile already exists in MongoDB
    existing_profile = db.profiles.find_one({"user_id": user_id})
    if existing_profile:
        # Update the existing profile
        db.profiles.update_one(
            {"user_id": user_id},
            {"$set": parsed_data}
        )
    else:
        # Save a new profile
        db.profiles.insert_one(parsed_data)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
