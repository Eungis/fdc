# [FastAPI self-learning]
- learn from lecture on udemy
    - course: *The complete FastAPI course with OAuth & JWT authentication*



## **1. Basic concept of API**
- What is an API?
- RestAPI
    - the data which is being fetched from the database is not sent to an API. Instead, the representation of the data is sent to the API and not the actual data. That's why it's called as REpresentational State Transfer.
    - what this does is that the API takes the current state of that particular data and it will transfer its representation and not the actual state.
- FastAPI
    - validates developers data type even in a deeply nested JSON requests
    - while creating a schema for your API, you can also define the data types of every field
    - supports building GraphQL API
    - built on standards like JSON, OAuth and OpenAPI
    - must faster to build/develop an API as compared to other frameworks

- wsgi vs asgi vs cgi
- unicorn vs gunicorn
- nginx vs apache
    - https://choiblog.tistory.com/47
