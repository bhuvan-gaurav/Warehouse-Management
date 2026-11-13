from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import functions    
from pydantic import BaseModel

app = FastAPI()

class PackageCreate(BaseModel):
    name: str
    destination: str
    weight: float
    arrival_date: datetime
    status: str = "pending"

class PackageResponse(BaseModel):
    id: int
    name: str
    destination: str
    weight: float
    arrival_date: datetime
    status: str
    batch_id: int

class DispatchBatchResponse(BaseModel):
    id: int
    vehicle: str
    destination: str
    dispatch_date: datetime
    status: str
    packages_dispatched: int

@app.post("/packages")
def Register_package(name: str, destination: str, weight: float, arrival_date: datetime, status: str, token: str = Header(None)):
    result = functions.register_package(name=name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    return result

@app.get("/packages/{id}")
def get_package(id: int):
    result = functions.get_package(id=id)
    return result

@app.patch("/packages/{id}")
def update_package(id: int, data: dict):
    result = functions.update_package(id=id, data=data)
    return result

@app.delete("/packages/{id}")
def delete_package(id: int):
    result = functions.delete_package(id=id)
    return result

@app.get("/packages")
def search_packages(destination: str = None, status: str = None, arrival_date: str = None, token: str = Header(None)):
    username=functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.get_all_packages(destination, status, arrival_date)
    return result

@app.get("/dispatch_batches")
def get_dispatch_batches(destination: str = None, vehicle_number: str = None, status: str = None, token: str = Header(None)):
    username=functions.verify_token(token=token, token_type="access")
    result = functions.get_all_dispatches(destination, vehicle_number, status)
    return result

@app.get("/packages/status")
def get_statistics():
    result = functions.get_summary()
    return result

@app.post("/dispatch_batches")
def create_dispatch_batch(destination: str, vehicle_number: str, status: str, package_ids: list):
    result = functions.add_dispatch(vehicle=vehicle_number, destination=destination, dispatch_date=None)
    return result

@app.post("/login")
def login(username = Body(), password = Body()):
    token = functions.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

@app.post("/refresh")
def refresh_token(token: str):
    username = functions.verify_token(token=token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    new_access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": new_access_token}

@app.post("/register")
def register_user(username = Body(), password = Body()):
    if functions.register_user(username=username, password=password):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")
