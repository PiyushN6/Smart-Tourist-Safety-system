from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from web3 import Web3
from hexbytes import HexBytes
from ..core.config import settings

router = APIRouter(tags=["blockchain"])

# Minimal ABI for DigitalIDRegistry.get(bytes32) -> (bytes32 idHash, address issuer, uint8 status)
ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "idHash", "type": "bytes32"}],
        "name": "get",
        "outputs": [
            {"internalType": "bytes32", "name": "idHash", "type": "bytes32"},
            {"internalType": "address", "name": "issuer", "type": "address"},
            {"internalType": "uint8", "name": "status", "type": "uint8"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

class VerifyOut(BaseModel):
    found: bool
    issuer: str | None = None
    status: int | None = None

@router.get("/verify", response_model=VerifyOut)
def verify(id_hash: str):
    if not settings.CONTRACT_ADDRESS:
        raise HTTPException(status_code=400, detail="contract not configured")
    try:
        w3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS), abi=ABI)
        # accept hex string with or without 0x
        hex_hash = id_hash if id_hash.startswith("0x") else "0x" + id_hash
        result = contract.functions.get(HexBytes(hex_hash)).call()
        # If idHash is zero, treat as not found
        found = any(int(b) != 0 for b in result[0])
        if not found:
            return VerifyOut(found=False)
        return VerifyOut(found=True, issuer=result[1], status=int(result[2]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
