from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test():
    """Test endpoint that returns hello world."""
    return "hello world!"
