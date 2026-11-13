from sqlalchemy import Integer, String, Float, Column, create_engine, DateTime
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

USERNAME = "Bhuvan"
PASSWORD = "Bhuvan123"

ACCESS_TOKEN_EXPIRY = 1
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(DateTime, default=datetime.now)
    status = Column(String)

class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status = Column(String)
    package_ids = Column(String)

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    role = Column(String)

Base.metadata.create_all(engine)

def add_package(name, destination, weight, status="pending"):
    session = Session(engine)
    pkg = Package(
        name=name,
        destination=destination,
        weight=float(weight),
        status=status
    )
    session.add(pkg)
    session.commit()
    response = {
        "id": pkg.id,
        "name": pkg.name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": pkg.arrival_date,
        "status": pkg.status
    }
    session.close()
    return response

def get_package(id):
    session = Session(engine)
    pkg = session.get(Package, id)
    if not pkg:
        session.close()
        return None
    response = {
        "id": pkg.id,
        "name": pkg.name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": pkg.arrival_date,
        "status": pkg.status
    }
    session.close()
    return response

def update_package(id, name=None, destination=None, weight=None, status=None):
    session = Session(engine)
    pkg = session.get(Package, id)
    if not pkg:
        session.close()
        return None

    if name is not None:
        pkg.name = name
    if destination is not None:
        pkg.destination = destination
    if weight is not None:
        pkg.weight = float(weight)
    if status is not None:
        pkg.status = status

    session.commit()
    response = {
        "id": pkg.id,
        "name": pkg.name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": pkg.arrival_date,
        "status": pkg.status
    }
    session.close()
    return response

def delete_package(id):
    session = Session(engine)
    pkg = session.get(Package, id)
    if not pkg:
        session.close()
        return "not_found"

    if pkg.status == "dispatched":
        session.close()
        return "dispatched"

    session.delete(pkg)
    session.commit()
    session.close()
    return "deleted"

def get_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    query = session.query(Package)
    if destination is not None:
        query = query.filter_by(destination=destination)
    if status is not None:
        query = query.filter_by(status=status)
    packages = query.all()
    if arrival_date is not None:
        filtered = []
        for pkg in packages:
            if str(pkg.arrival_date.date()) == arrival_date:
                filtered = filtered + [pkg]
        session.close()
        return filtered
    session.close()
    return packages

def get_warehouse_analytics():
    session = Session(engine)
    total_received = session.query(Package).count()
    total_pending = session.query(Package).filter_by(status="pending").count()
    total_dispatched = session.query(Package).filter_by(status="dispatched").count()
    packages = session.query(Package).all()
    destination_wise = {}
    for pkg in packages:
        if pkg.destination in destination_wise:
            destination_wise[pkg.destination] = destination_wise[pkg.destination] + 1
        else:
            destination_wise[pkg.destination] = 1
    session.close()
    return {
        "total_received": total_received,
        "total_pending": total_pending,
        "total_dispatched": total_dispatched,
        "destination_wise": destination_wise
    }

def verify_login(username, password):
    session = Session(engine)
    user = session.query(User).filter_by(user_name=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    role = user.role
    session.close()
    access_token = create_token(username=username, role=role, token_type="access")
    refresh_token = create_token(username=username, role=role, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token, "role": role}

def create_dispatch_batch(destination, vehicle, package_ids, dispatch_status="scheduled"):
    session = Session(engine)
    batch = DispatchBatch(
        destination=destination,
        vehicle=vehicle,
        dispatch_status=dispatch_status,
        package_ids=package_ids
    )
    session.add(batch)
    if package_ids is not None:
        for pid in package_ids.split(","):
            pkg = session.get(Package, int(pid))
            if pkg is not None:
                if dispatch_status == "dispatched":
                    pkg.status = "dispatched"
                else:
                    pkg.status = "in_batch"
    session.commit()
    response = {
        "id": batch.id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "dispatch_status": batch.dispatch_status,
        "package_ids": batch.package_ids
    }
    session.close()
    return response

def get_dispatch_batches(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)
    query = session.query(DispatchBatch)
    if destination is not None:
        query = query.filter_by(destination=destination)
    if vehicle is not None:
        query = query.filter_by(vehicle=vehicle)
    if dispatch_status is not None:
        query = query.filter_by(dispatch_status=dispatch_status)
    batches = query.all()
    session.close()
    return batches

def create_token(username, role, token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "username": username,
        "role": role,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False
    if payload["token_type"] == token_type:
        return {"username": payload["username"], "role": payload["role"]}
    return False

def register_user(user_name: str, password: str, role: str = "staff"):
    session = Session(engine)
    user_exists = session.query(User).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(User(user_name=user_name, password=ph.hash(password), role=role))
    session.commit()
    session.close()
    return True