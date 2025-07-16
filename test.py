import asyncio
import uuid
import httpx



async def fetch_batch_data(cookie, notification_id='5d8310af-4762-f011-bec3-6045bd8a1ab6'):
    BATCH_ID = f"batch_{uuid.uuid4().hex}"

    BATCH_BODY = f"""--{BATCH_ID}
        Content-Type: application/http
        Content-Transfer-Encoding: binary

        GET /api/data/v9.0/emails({notification_id})?$select=safedescription HTTP/1.1
        Accept: application/json
        """
    url = "https://goto.crm4.dynamics.com/api/data/v9.0/$batch"
    headers = {
        "Content-Type": f"multipart/mixed;boundary={BATCH_ID}",
        "Accept": "application/json",
        "Cookie": cookie
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=BATCH_BODY.encode())
            response.raise_for_status()
            print("resp:", response.text)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response}")
    except Exception as e:
        print(f"Other error: {e}")

async def main():
    await fetch_batch_data()

if __name__ == "__main__":
    asyncio.run(main())
