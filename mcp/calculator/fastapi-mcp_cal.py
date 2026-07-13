from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(title="fast api calc")

@app.get("/")
def hello():
    return {"message":"hello dude,all are right"}
    
@app.post("/multiply")
def multiply(a:float,b:float):
    """
    It enables us to multiply twho number
    params a and b return a*b
    """
    result = a*b
    return {"result":result}

@app.post("/add")
def add(a:float,b:float):
    result =  a + b
    return {"result":result}

@app.post("/substract")
def substract(a:float,b:float):
    """
    Its role is to substract 2 number
    """
    result = a - b
    return {"result":result}

@app.post("/divide")
def divide(a:float,b:float):
    """
        here we divide two number
    """
    if b == 0:
        return {"result":"b must be different of 0"}
    result=  a/b
    return {"result":result}


# Convert it to a fastapi
mcp = FastApiMCP(app,name="FastApi mcp calculator")

mcp.mount_http()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8002)
