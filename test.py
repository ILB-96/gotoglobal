
import asyncio
import httpx


async def fetch_data(request_url: str):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-ms-client-request-id": "c0e00940-28a3-4eb9-9d5b-2529abba5c42",
        "x-ms-client-session-id": "45a6df40-b40a-4e5e-b672-aac39886e717",
        "x-ms-correlation-id": "eac521a0-c393-47d0-bb95-8d93e8d24e28",
        "x-ms-sw-objectid": "b463b0ad-ff4f-4dca-8309-538adb5f5f7d",
        "x-ms-sw-tenantid": "d2256e74-8ec1-47b1-ae18-873765a27e8b",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(request_url,headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Request error: {e}")
        return {}

async def main():
    url='https://autotel.crm4.dynamics.com/api/data/v9.0/appnotifications?partitionId=05aa52f5-23e2-ef11-8eea-7c1e5262002b&$top=100&$select=appnotificationid,title,body,data,priority,icontype,toasttype,createdon,modifiedon&$filter=%20ownerid/ownerid%20eq%2005aa52f5-23e2-ef11-8eea-7c1e5262002b%20and%20createdon%20gt%202025-07-12T15:04:25.394Z%20and%20createdon%20le%202025-07-12T15:10:44Z&$orderby=createdon%20desc'
    data = await fetch_data(url)
    print(data)
    
if __name__ == "__main__":
   url='https://autotel.crm4.dynamics.com/api/data/v9.0/appnotifications?partitionId=05aa52f5-23e2-ef11-8eea-7c1e5262002b&$top=100&$select=appnotificationid,title,body,data,priority,icontype,toasttype,createdon,modifiedon&$filter=%20ownerid/ownerid%20eq%2005aa52f5-23e2-ef11-8eea-7c1e5262002b%20and%20createdon%20gt%202025-07-12T15:04:25.394Z%20and%20createdon%20le%202025-07-12T15:10:44Z&$orderby=createdon%20desc'
   asyncio.run(main())