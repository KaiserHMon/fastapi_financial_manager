import httpx
from fastapi import HTTPException

BASE_URL = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0"

DESIRED_CURRENCIES = ["Dolar", "Euro", "Real"]

async def get_exchange_rates():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/Cotizaciones")
            response.raise_for_status()
            rates = response.json()
            
            filtered_rates = [
                rate for rate in rates
                if any(currency in rate.get("descripcion", "") for currency in DESIRED_CURRENCIES)
            ]
            
            return filtered_rates
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error getting exchange rates from BCRA")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to BCRA API: {e}")