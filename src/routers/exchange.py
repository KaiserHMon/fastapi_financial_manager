from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ..services import exchange_services

exchange = APIRouter(prefix="/exchange", tags=["Exchange"])

@exchange.get("/", response_model=List[Dict[str, Any]])
async def get_exchange_rates():
    return await exchange_services.get_exchange_rates()

@exchange.get("/dollar", response_model=Dict[str, Any])
async def get_dollar_rate():
    rates = await exchange_services.get_exchange_rates()
    for rate in rates:
        if "Dolar" in rate.get("descripcion", ""):
            return rate
    raise HTTPException(status_code=404, detail="Dollar rate not found")

@exchange.get("/euro", response_model=Dict[str, Any])
async def get_euro_rate():
    rates = await exchange_services.get_exchange_rates()
    for rate in rates:
        if "Euro" in rate.get("descripcion", ""):
            return rate
    raise HTTPException(status_code=404, detail="Euro rate not found")

@exchange.get("/real", response_model=Dict[str, Any])
async def get_real_rate():
    rates = await exchange_services.get_exchange_rates()
    for rate in rates:
        if "Real" in rate.get("descripcion", ""):
            return rate
    raise HTTPException(status_code=404, detail="Real rate not found")