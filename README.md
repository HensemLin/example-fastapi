# Learning FastAPI Project

This project serves as a learning experience for FastAPI, featuring multiple routers for authentication, CRUD operations on posts, user creation, and post voting.

## Project Structure

The FastAPI application consists of four main routers:

1. **auth:** Handles authentication.
2. **post:** Manages CRUD operations for posts.
3. **user:** Facilitates user creation.
4. **vote:** Allows users to vote on posts.

## Database Schema

The MySQL database used in this project does not enforce a specific schema for posts.

## API Usage

### Authentication

#### `POST /login`

Endpoint for user authentication.

### Posts

#### `GET /posts/`

Retrieve a list of all posts.

#### `POST /posts/`

Create a new post.

#### `GET /posts/{id}`

Retrieve details of a specific post.

#### `DELETE /posts/{id}`

Delete a specific post.

#### `PUT /posts/{id}`

Update a specific post.

### Users

#### `POST /users/`

Create a new user.

#### `GET /users/{id}`

Retrieve details of a specific user.

### Voting

#### `POST /vote/`

Vote on a post.

## Examples

No specific examples are provided. Users are encouraged to explore and experiment with the provided endpoints based on their learning goals.

## Configuration

No special configurations or environment variables are required. The project runs as a standard uvicorn app.

## Testing

To run tests, use the following command:

```bash
pytest
```

## Run the App

To run the apps, use the following command:

```bash
uvicorn app.main:app --reload
```
