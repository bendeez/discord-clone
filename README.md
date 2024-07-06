
# Discord Clone
* FastAPI - Backend
* React - Frontend
* Websockets - Real time communication

## Here's a demo of the application:
https://github.com/bendeez/my-discord-clone/assets/127566471/3df75063-b85d-4055-9783-1d1b98d1cbac

## Want to run this?:
1. Copy and paste these env variables into a file named .env.dev and put it in the backend/app directory:
   ```env
    JWT_SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
    JWT_ALGORITHM=HS256
    DATABASE_NAME=discord
    DATABASE_PORT=5432
    DATABASE_USERNAME=postgres
    DATABASE_PASSWORD=discord
    DATABASE_HOST=postgres
    FIREBASE_CONFIG='{}'
    REDIS_HOST=redis
    REDIS_PORT=6379
   ```
**Heres a vid on how to get the firebase config:**
[Watch the video](https://www.youtube.com/watch?v=YOAeBSCkArA&t)

2. Run this command:
   ```sh
   docker-compose -f docker-compose.dev.yaml up
   ```
If you would like to message me, my discord is: **backendblaziken**