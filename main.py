from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import functions    

app = FastAPI()

@app.post("/packages")
def Register_package(name: str, destination: str, weight: float, arrival_date: datetime, status: str):
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
def search_packages(destination: str = None, status: str = None, arrival_date: str = None):
    result = functions.get_all_packages(destination, status, arrival_date)
    return result

@app.get("/dispatch_batches")
def get_dispatch_batches(destination: str = None, vehicle_number: str = None, status: str = None):
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