

from fastmcp import FastMCP

mcp = FastMCP(name="Calculator")

@mcp.tool()
def multiply(a:float,b:float):
    """
    It enables us to multiply twho number
    params a and b return a*b
    """
    return a*b

@mcp.tool(
    name="add",
    description="add two number",
    tags=["maths","arithmetic"]
)
def add(a:float,b:float):
    return a + b
    
@mcp.tool()
def substract(a:float,b:float):
    """
    Its role is to substract 2 number
    """
    return a - b
    
@mcp.tool()
def divide(a:float,b:float):
    """
        here we divide two number
    """
    if b == 0:
        return "b must be different of 0"
    return a/b

print("worked")

if __name__=="__main__":
    mcp.run()