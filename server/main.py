from fastapi import FastAPI

app = FastAPI(
      title="Book App Server",
      description="Book App",
      version="0.1.0",
      license_info={
          "name": "MIT",
          "url": "https://opensource.org/licenses/MIT",
      }
  )

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/books/{isbn}")
async def post_isbn(isbn):
    print(isbn)
    return {"isbn": f"Your ISBN : {isbn}"}
