from fastapi import APIRouter

router = APIRouter()


@router.get(
    '/',
    summary='Hello, world'
)
async def hello_world():
    return {'hello, world'}
