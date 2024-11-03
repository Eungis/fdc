import json
import ssl
import aiohttp
import asyncio
from contextlib import asynccontextmanager

# Create only one session per script
session = None


async def release_session(session: aiohttp.ClientSession):
    if all(
        # Current_tasks() means the main function that executes asynchronous running
        # In this case: aquery_multiple_es
        [t.done() for t in asyncio.all_tasks() - {asyncio.current_task()}]
    ):
        print("Release Session ... ")
        await session.close()
    else:
        print("Remaining tasks are not fininshed yet.")


@asynccontextmanager
async def get_session(es_id: str = None, es_pw: str = None, ca_cert_path: str = None):
    global session

    ssl_context = ssl.create_default_context(cafile=ca_cert_path) if ca_cert_path else None
    auth = aiohttp.BasicAuth(es_id, es_pw) if es_id else None

    if session is None or session.closed:
        # TCPConnector helps in maintaining a pool of open connections,
        # making multiple requests more efficient by reusing these connections instead of creating a new one each time.
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=5,  # Default: 0 (unlimited), which means limit is the only restriction.
            force_close=False,
            enable_cleanup_closed=True,  # Enables background cleanup for closed connections.
            ttl_dns_cache=300,  # Caches DNS lookups to speed up repeated connections to the same host.
            # ssl_context=ssl_context, # Here to comment it because the local es server does not require ssl connection
            # verify_ssl=True,
        )

        # Create session if no session specified
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=120),
            raise_for_status=True,
            # auth=auth, # # Here to comment it because the local es server does not require authentication
        )

    try:
        yield session
    finally:
        await release_session(session)


async def aquery_es(
    body: dict,
    url: str,
    headers: dict,
    es_id: str,
    es_pw: str,
    ca_cert_path: str,
):
    async with get_session(es_id, es_pw, ca_cert_path) as session:
        async with session.get(url, headers=headers, data=json.dumps(body)) as response:
            if response.status == 200:
                result = await response.json()

                # Preprocess the result
                for hit in result["hits"]["hits"]:
                    print(f"ID: {hit['_id']}, Score: {hit['_score']}, Source: {hit['_source']}")
            else:
                print(f"Query failed with status code {response.status}")
            return result


async def aquery_multiple_es():
    global session

    # Create tasks for all messages
    tasks = [
        aquery_es(
            body={},
            url="http://localhost:9200/movies/_search?pretty",
            headers={"Content-Type": "application/json"},
            es_id=None,
            es_pw=None,
            ca_cert_path=None,
        )
        for _ in range(10)
    ]

    responses = await asyncio.gather(*tasks)

    while asyncio.all_tasks():
        await release_session(session)
        if session.closed:
            break

    return responses


if __name__ == "__main__":
    # --------------- Run single query --------------- #
    # asyncio.run(
    #     aquery_es(
    #         body={},
    #         url="http://localhost:9200/movies/_search?pretty",
    #         headers={"Content-Type": "application/json"},
    #         es_id=None,
    #         es_pw=None,
    #         ca_cert_path=None
    #     )
    # )

    # --------------- Run multiple queries --------------- #
    asyncio.run(aquery_multiple_es())
