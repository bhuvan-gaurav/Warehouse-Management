from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import functions    

app = FastAPI()

GENRES = ["textbook", "fiction", "reference", "magazine", "biography"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get("/books/{book_id}")
def get_book(book_id: int):
    results=functions.get_book(book_id = book_id)
    if not results:
        raise HTTPException(status_code=404, detail="Book not found")
    return results


@app.post("/books")
def add_book(title: str, author: str, total_copies: int, genre: str):
    if title=="" or author=="" or genre=="":
        raise HTTPException(status_code=422,detail="Fields can't be empty")
    if total_copies<1 or total_copies>20:
        raise HTTPException(status_code=422,detail="total_copies must be between 1 and 20")
    if genre not in GENRES:
        raise HTTPException(status_code=422,detail="Invalid genre")
    result= functions.add_new_book(title=title, author=author, total_copies=total_copies, genre=genre)
    return result

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    result=functions.delete_book(book_id=book_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Book not found")
    if result=="on_loan":
        raise HTTPException(status_code=400,detail="Book has copies out on loan")
    return result

@app.get("/books")
def menu(genre: str = None, title: str = None):
    if genre is not None and genre not in GENRES:
        raise HTTPException(status_code=422,detail="Invalid genre")
    result= functions.get_all_books(genre=genre, title=title)
    return result

@app.patch("/books/{book_id}")
def update_total_copies(book_id:int,total_copies:int):
    result=functions.update_total_copies(book_id=book_id,new_total_copies=total_copies)
    if result is None:
        raise HTTPException(status_code=404,detail="Book not found")
    if result=="below_loans":
        raise HTTPException(status_code=400,detail="Total copies below copies on loan")
    return result

@app.patch("/loans/{loan_id}/return")
def return_loan(loan_id: int):
    result=functions.loan_return(loan_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Loan not found")
    if result=="already_returned":
        raise HTTPException(status_code=400,detail="Loan already returned")
    return result

@app.patch("/loans/{loan_id}/renew")
def loan_renew(loan_id: int):
    result=functions.loan_renewal(loan_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Loan not found")
    if result=="already_returned":
        raise HTTPException(status_code=400,detail="Loan already returned")
    if result=="already_renewed":
        raise HTTPException(status_code=400,detail="Loan already renewed")
    if result=="overdue":
        raise HTTPException(status_code=400,detail="Loan is overdue")
    return result

@app.get("/loans/student/{roll_no}")
def loan_student(roll_no: str):
    result=functions.student_loans(roll_no)
    if result is None:
        raise HTTPException(status_code=404,detail="Student not found")
    return result

@app.get("/loans/overdue")
def overdue():
    result=functions.loans_overdue()
    return result


@app.post("/loans")
def borrow(book_id: int, roll_no: str):
    if roll_no == "":
        raise HTTPException(status_code=422, detail="Roll number can't be empty")
    result = functions.borrow_book(book_id, roll_no)
    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if result == "no_copies":
        raise HTTPException(status_code=400, detail="No copies available")
    if result == "max_loans":
        raise HTTPException(status_code=400, detail="This student already has 3 books.")
    if result == "has_overdue":
        raise HTTPException(status_code=400, detail="Student has an overdue loan")
    if result == "already_has":
        raise HTTPException(status_code=400, detail="Student already has this book")
    return result