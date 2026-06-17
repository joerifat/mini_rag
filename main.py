from fastapi import FastAPI

app= FastAPI()


def welcome():
    return {"message": "Welcome to the FastAPI application!"}