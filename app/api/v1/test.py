from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test():
    """Test endpoint that returns hello world."""
    return "hello world!"

@router.get("/test2")
async def test2():
    """Test endpoint that returns itu."""
    return "itu"