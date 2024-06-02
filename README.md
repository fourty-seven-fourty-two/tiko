# Setup
## Docker
Run `docker-compose up` - API will be available at "http://localhost:8000"
## Local setup
1. Install poetry
```
pip install poetry
```
2. Install dependencies
```
poetry install
``` 
3. Configure env variables
```
cp .env.dev .env
```

# Assumptions
* only authenticated users can view events
* user who created an event doesn't count as its attendee
* we don't want infinite capacity for event (limited to 1 million)
* we don't need optimization and it is fine to use the same serializer for list and detail requests
* it is OK to use built-in user model
* for now, we can use limit/offset pagination without considering performance drawbacks
* we don't need no complex infrastructure to run the app (uWSGI and Nginx)

# Implementation Checklist
Documentation could be found at http://localhost:8000/api/schema/swagger-ui/
## Users must be able to register an account
Endpoint: `/v1/profile/signup/`
## Users must be able to log in into their account 
A system of token rotation must be implemented. For this the API needs to provide a user with access_token and a refresh_token, as well as a way to refresh and validate the access_token. The lifetime of the access_token should be 1 hour and the lifetime of the refresh_token 1 day
Endpoints: `/v1/profile/token/`, `/v1/profile/token/refresh/`
## Events CRUD
Endpoint: `/v1/events/`
## Users must be able to register to an event or un-register. 
This can only be done in future events and not in past events.
Endpoints: `/v1/events/{event_id}/attend/` and `/v1/events/{event_id}/cancel/`
## Documentation of your code, API docs (swagger or other)
Documentation could be found at http://localhost:8000/api/schema/swagger-ui/
## Tests
To run tests locally, do `pytest .`. To run them in docker-compose, run `docker-compose run --entrypoint="pytest ." --rm api`
## Add logic to manage an event capacity. 
> if event reaches maximum number of registered attendees, an error should be returned to a user trying to register.

Capacity can be set / updated as a part of event creation 
## Add some  filtering to endpoints retrieving events 
(e.g. date , type, status, past events, future events, etc)
Event list endpoint has following filters (as query parameters):
- attending=true - filter events user decided to attend
- created=true - filter events created by user
- starts_after=datetime - filter events that starts after certain date
- starts_before=datetime - filter events that starts before certain date
- status=<value> - shortcut to filter by status (past, ongoing, upcoming)
