import asyncio
import traceback
from typing import Dict
import uuid
import httpx



async def fetch_batch_data(mode, cookie, notification_id='27b54f82-ee5d-f011-bec2-7c1e5283c999'):
    BATCH_ID = f"batch_{uuid.uuid4().hex}"

    BATCH_BODY = (
        f"--{BATCH_ID}\r\n"
        "Content-Type: application/http\r\n"
        "Content-Transfer-Encoding: binary\r\n"
        "\r\n"
        f"GET /api/data/v9.0/emails({notification_id})?$select=safedescription HTTP/1.1\r\n"
        "Accept: application/json\r\n"
        "\r\n"
        f"--{BATCH_ID}--\r\n"
    )

    url = f"https://{mode}.crm4.dynamics.com/api/data/v9.0/$batch"
    headers = {
        "Content-Type": f"multipart/mixed;boundary={BATCH_ID}",
        "Accept": "application/json",
        "Cookie": cookie
    }
    print(f"url: {url}, headers: {headers}, body: {BATCH_BODY}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=BATCH_BODY.encode())
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response}")
    except Exception as e:
        print(f"Other error: {e}")
        traceback.print_exc()
        
async def fetch_data(request_url: str, x_token: str, payload: Dict) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Token": x_token
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(request_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Request error: {str(e)}")
        return {}
async def main():
    # url = 'https://autotelpublicapiprod.gototech.co/API/SEND/GetAllCars'
    # payload = {
    #     'Data': 'null/null/1/false',
    #     'Opcode': 'GetAllCars',
    #     'Username': 'x',
    #     'Password': 'x'
    # }
    # data = await fetch_data(url, 'D4B6DBF95BF0CC112ED2F836356DE6A5354418D8E4CF853EE084CC5344367FD2F8DE7FE735C3342658DF2BF6D3E0C4C1', payload)
    # print(data)
    cookie = 'CrmOwinAuth=chunks:2; CrmOwinAuthC1=MAAAAEqzwZNbWRHwjuN8HlI1xOekETSQRVNDhpSgsfbqvdIJEzWEYbfQ6CAcjrSmNEpTZx-LCAAAAAAABADFWVuP48aV7nZPxvYkayQI4JfAwABr-CETSrxfjB0kJEXdWqIkUheSLwLJKt5vYpGiqJ-xD_tb9gft2_6Jpbo9Hs_E2HUs7YTopkqHVd85PHXq1PlKD3d3d18tmjCT8zwOoVhXwf3d_Z3QiR_sGnyLP18cdrk_39x3rXfX_d3boKoK9H2_jyrU68BA3qBeBqs-IEmGhRyN8dAlMJpzCMyGBI_xHMWxjE1ykHf693cPIULXYlw7_oXtutU9_ucLTIfSNE2voXp56fdJHCf6xnymuwFM7X8Nswr6sKTIazV-aXfe3ldhCl8RHM0yFMGy7CfU_9LdBzYKvgaApti1G83SRR7UAMNjJhD96z36B9cu8iQEaJ_YFXQ6gG9tinQYF1AYJD0co0EXSbzD8phDusDzSJqyOXC94s9c97_u5XQw4tnTwYL5LJ-Y6y2JwCSl-k2Cu7QbrYdAm_bt4yKWJIimnDJaOtpo54Yhi1iinC-Gj8x8EOF8C_gSzoMoF8klnsnDN5GWWiEf0VvEsAKLU7vV1NQLxy-ydsgtNOaIfHjuU9qB1gcpOIKRkDkjITR3TW2SQjUKJo-KtD7G_Jvp7M1UDVZG_zGC6pJtQsXPV2-orZcbAU4rC1KeHMYKYmJxMJG17YYWN5OpvBJRkdq7UCAm17vq7Q_hhp5iC_VOaYJyu3iKuwZdQo_pd38hgFkVVm3fTewwRX1Ul5mdws8lu0xtN77ejr_-Ojv88AiziyUvJ6i0YXK9Ib8JQdUWL2oEy-vBXoaFDUD5O4roEQzdo9kexV-P-irJ_TDbB10i-I_7RU8OtVAdmGczkgJLJlKrC9DZWotNUqkWg3mz0HFifg4CazQhrGibquRKn45W7TzakNbaxWfrIDHPSqUOQDjXicBaK_Rs7VPzs0uqO6VVyQ1tBjmwDbU1d1s0S6eBmxKBSVaiRQq4QwLkkNPAkZnIIXG_XSlvb5COL7P61fOsvr5ZmH0c7mnoljnKvarn5unfRVfuRNCtnqVeCMtvHZqlHNwGmOfRXpe-XBvjKVzAGIq3gcN4jHeL9PUqz4oSpnsUAkzHCIzBSALjSZ4kSb7biSmS6PIOw3Rpk-JwQuiGChxGCgJ7A68XdQh-T-A41a04miY5aqCQzA02-O5dulqCJCDnCphDOTRGelSX_G3ewXjccz2SczmHu4Gq36HQz7rlgapu0_kCHN19mvk3mJW_xwVpdGvc34ZZnOVNllXNDaL9A-gXcYrC6zEHvy5RX1bz-4X0pvQ8PPRmC3NpckNDZVxYLY-2ODVP50LU_HIwwo4jZKoGo1xv8h8rmNlZtS-hH-adN9y8gJ8pm-uBmX8omzxb0a2DX4J-vXH3d9-ET9mz5zxnz7_5eZX7Se7YycW-6zUIvy4U6iL7_7bs4QjLB6J3A2byounq128dTvAcjwYYBT0Bo1lewHiCpjCOdQiBhjzD4ML1uj4_pWjv2vCeuEHl8YTlPsjLG4D9_gLmhUkFy303Gp4-o7nrUb-4oKaFG74kGaELlk_IfJ483Wl-QbGfVO_TrJTgK7xHk7PElLSQEF3xRpGDUHqLyHmalgaF1QuC_6TOeTgx1Z9k9YgvJpTWHJLxUNlmdj4XUSCPSUO5pLSuVxyC_7vX13lnQM8t096FY1d53KWgtoA_c9Jxf8f9r1n8h6R1gcm6NkIl9GAJM_cmy_Q3dlGEn-qU5YsnZbZb3pO3rwM-9BqJE2S_CxMAj6EL3byLkVP1zpc_KagJnGFoHqc7PZyN0QTJYAKETJdnKcrtBpIue4OSkPyH9umn-uDfH6RLmGQ-Eosi72I87Tr1NGiDXRlWsCcmyWvZTmAG7BI9yXt6YJcQfCR96v1zsh-7B3aWwWQOEbJ9-Iz0BP6hXO_GX2RVTy6hfYG8tC-9n1ofdBuGCfyp9o--P8GPyrwuPpJNMi_v9uOqK5KWZV5dqE_XypPQbZ81ze0w-Qnu5auTn3RYVRdHPfdZZEmYwTmE72XPvZclRJdl8_4V9U78sV2bjnc_A_3YkmwUupeHNzgYKgOB6Ik6L4IRneBotEAbWI8mLmXZUyxsXPHd1fzYkpGoN0dR7F2v_vtfnGlSWHWM-32uQQ8lsm9xzmpXrwiOIQWap5lfftbI0ldrzhzvn6QZnopnzQxFsvSn1GyH-X9-JsKVOOrz1iWWtrS0yzPfG6zVMQnk_gTkjELbi6gvDvXleTfiJutqiVpFX2y4TFs4wkLp6wBkamduqh38N1I0oBbBGpqKI7mbQbfnz93iPGac_GgI9jaNLaK_Us4ns8kXihrYWmvg1SbjLQg2qJUnulQ92tohPFjtRHacN4uaqgOVJ1cSfBwfdiOaHaHDSp7QtdG2mSmWA9ppiPVsyQB147fu0jxZ1qRduy4v9iMNCjnA5aHGnCdTbSDa6400pw4gFWpCHZ4NhaKpo63xuVGTo_NRhfnSl_zjFIUncsipXm0xalCwR2Nl2rymCs500taGM9ds_wZHSNcst6K5AbV_qKvw6yjbjcPaj5l4IYFd5uLbTRcLN6r5vAr8bcC1jb_0tOWp3uKFMcZKaA2ZLIq3lDrBpssphgxVnBltTEuWsW0dSkoAuT0DmYhdkjhfb8qXF1NCUMLkBYW_vkFZdAEEbbYvq_9-9avzteiLktgonUjalnoB652danZKRuKQMLSVIjaDrtDdiMISE12mmBm4a-3xxVrV1qjcjivm6JDsWC1dduhtgvn8RAbnQcz62yhouPyw3xw1LRkLJjWfqnhViuNoFhMDlGZkIB21Ab1ZBvhoKUIghLOluwGUIRTrPQM05KrtIdoajLmnYjE1pSYPxxohjJoBiPfueRaoLn2kJGE084XItkhSXHqTAbvczhl5uLe8tMFW4qY9lYERgT0_ktIS5kxTppxs8JKoHJmIlCaNxO5gEo0Na4t4opkSsUPCWjqp0loZzkB1Th8Ld1wLRFyVo3TkCPFo7DHQDJhmgxFFwT5yGq2V89MprlSbEXRoj2OJLCcKGE0zpCmAPYy9PLRFdzekNX2U2mvRKmvEDUlNlB6Py9BtZpGxIxQXiGbCOW3g1YS_96fTZbZXTD9hgxlNnwJXpOFO9HRfiwpycNgOhnlxWs6XRhk2GtjafLHQAzTgQyBje0Mu-BaKlWjZy-2AkTdunuzCZBqIgb_O93CL7fIkGMonSjABHeoB7QePDRUgE1j7Wl-rTJ0Vi1MY28JCMvjltFUBVBZ-kMvcmqOIQgzG55FJW5goOqcAq82FPTnTFMUvmR3pD6aOzzSPS9yZh9ZuFEWrWMZ4PVqjXZTIk_S4QN4joyJZI9sIHU9nJZvFC2_AEoLftk5cli3GDeRCpM4OcoRSDwp1vtsDYsBL0j7E0sNgTCPaN7qiVQyVYNSU4-2QiqPYOpinx3peGf4x2axiZSrWJy0tObwoCntJTx9dP-Jm7Yo6YwFwnfEjv4nhakV1Vd2w2q1t2_EYz-DkqnAsxtGSMp3MzL2Ax9LAoYsc24Hanw2TudbkwmQyfUy7quwQPB5qBpf2HkMLluXMVf2sY1wTSqsBX57kjlh1rO1xMGWnGGxVS0bbmDKbw6jbT5jOgHVtAdyna9pVkQ7lozSpQ8w4FOe8zjSzWFgr0xKiIhJTkUxgMJsHpJLViTrfeMY0LOcZha3XUyaXH4vJWW8XJ6zmBrq33adbY7PeZptwbLAj8Sx6klHz4ZjlhxtjrBaypCARDeWEiOtQlfmC0gNCt9KFnsXAtLo13-5kMVuscHNzdg-qOyOoLABtyyhKDkIqUkcshbZyKK4NrzmwPE9px6gwhht; CrmOwinAuthC2=aWS98eTCtYW7xsl4oA3EpWYclC4fJOIKLcO6cllBrzuZx1rbG0S51JwXy0WtBxJ6SVHTDYb3amSbTJD5z4MiMWQ5LuIOYUi4xl6iN_Bynrhlrxsxzpbk18UCz5U6bY3yMSjcuI1IOCI8xUvoYshEY-SMHT8dg7Eiz6ZTWpHhw5omdnFbaIJJXEp_qm32pjPDOVSAeI_2URtY8Xc525LyW4gDwYsNq4-0GnZpnPvzqh-Trlz_WihzDfvgs-Zlnl-tyf9n9f9nruE1YdhTi_G4ruJzxXRg53esA7G4vRk_bcGp3RN1GxemvT-z0Le6xros7HnYJVwzyRLdDdJXbhQoDyqZZmsH57zqe4sKNPHlLfFd0tOdC7d8iaJdu8N3zx7qjm2__pYc6WtRxGP1y_v2Lfn74Y6-rFdxYfx43GZZ2Cv_t3Rs8_ez2vorIn5jOcy2Rp2me9fNLMUH2nyB-UP3bXgFLFKKqo493X_S6WrTzCvpGr7O_vMbZjkK1r0mcYl4TxPc08T1Fvx7N15_3QoRqCL5Z1_AnvcgPe_0PoEovXbohAAA;'
    data = await fetch_batch_data('autotel', cookie, '54aa96b4-b764-f011-bec3-000d3ac29661')
    print(data)
    
if __name__ == "__main__":
    asyncio.run(main())
