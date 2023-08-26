[![Python tests](https://github.com/wim-vdw/flask-etag/workflows/Python%20tests/badge.svg)](https://github.com/wim-vdw/flask-etag/actions?query=workflow%3A%22Python+tests%22)
# Flask ETag implementation1
Implementation of `ETag` (entity tag) for a resource in Flask (Python) in a RESTful API. The `ETag` hash is generated based on the change date of the resource.

ETags can be useful in the following scenarios:
- To cache unchanged resources (client-side caching).
- To avoid mid-air collisions (prevent simultaneous updates of a resource from overwriting each other -> optimistic concurrency control).

Reference: [ETag - HTTP | MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag)

## Installation instructions
Make sure Python >=3.7 is installed (important because `Python f-strings` are used).
Clone this repository and navigate to the directory containing this repository.

Prepare the Python virtual environment containing the required packages:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ python -m pip install --upgrade pip setuptools
$ pip install -r requirements.txt
```

## Start the Flask server
Make sure the Python virtual environment is activated, set the environment variable `FLASK_APP` pointing to the Flask application and run the Flask server:
```bash
$ source venv/bin/activate
$ export FLASK_APP=myapp
$ flask run
```

## Caching of unchanged resources (curl example)
Create a new person:
```bash
$ curl --request POST --include \
  localhost:5000/persons \
  --data '{"person_id": "1", "person_name": "Wim"}'
```
Results in a status code `201` and the generated `ETag` in the response header:
```bash
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 96
ETag: "42e98b50d35eb07fc6d595d019cc91c7"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 10:11:52 GMT

{
  "change_date": "2020-12-24T10:11:52.200311",
  "person_id": "1",
  "person_name": "Wim"
}
```
Retrieve the person without using the `ETag`:
```bash
$ curl --request GET --include \
   localhost:5000/persons/1
```
Results in a status code `200`, the `ETag` in the response header and the complete response in `JSON`:
```bash
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 96
ETag: "42e98b50d35eb07fc6d595d019cc91c7"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 10:26:37 GMT

{
  "change_date": "2020-12-24T10:11:52.200311",
  "person_id": "1",
  "person_name": "Wim"
}
```
Retrieve the person with the `ETag` in the `If-None-Match` request header:
```bash
$ curl --request GET --include \
   localhost:5000/persons/1 \
   --header "If-None-Match:42e98b50d35eb07fc6d595d019cc91c7"
```
Results in a status code `304` and no response in `JSON` (client-side caching saves bandwidth):
```bash
HTTP/1.0 304 NOT MODIFIED
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 10:16:37 GMT
```

## Avoiding mid-air collisions (curl example)
Create a new person:
```bash
$ curl --request POST --include \
  localhost:5000/persons \
  --data '{"person_id": "2", "person_name": "Wim"}'
```
Results in a status code `201` and the generated `ETag` in the response header:
```bash
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 96
ETag: "5f190e4939a582ca96aeefb8e2d5ee2c"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 14:01:26 GMT

{
  "change_date": "2020-12-24T14:01:26.095555",
  "person_id": "2",
  "person_name": "Wim"
}
```
Perform a first update of the person with the `ETag` in the `If-Match` request header:
```bash
$ curl --request PUT --include \
   localhost:5000/persons/2 \
   --data '{"person_name": "Wim - update 1"}' \
   --header "If-Match:5f190e4939a582ca96aeefb8e2d5ee2c"
```
Results in a status code `200` and a new generated `ETag`in the response header:
```bash
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 107
ETag: "b90595e3eae35cf10cc427cd85b264da"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 14:02:40 GMT

{
  "change_date": "2020-12-24T14:02:40.897605",
  "person_id": "2",
  "person_name": "Wim - update 1"
}
```
Perform a second update of the person with the `ETag` from the initial creation in the `If-Match` request header:
```bash
$ curl --request PUT --include \
   localhost:5000/persons/2 \
   --data '{"person_name": "Wim - update 2"}' \
   --header "If-Match:5f190e4939a582ca96aeefb8e2d5ee2c"
```
Results in a status code `412` and a `JSON` response message to indicate that the resource was already changed:
```bash
HTTP/1.0 412 PRECONDITION FAILED
Content-Type: application/json
Content-Length: 81
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 14:03:44 GMT

{
  "message": "Data already changed, get recent resource data and ETag first"
}
```
Retrieve the most recent person data again:
```bash
$ curl --request GET --include \
   localhost:5000/persons/2
```
Results in a status code `200`, the most recent `ETag` in the response header and the most recent resource data in `JSON`:
```bash
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 107
ETag: "b90595e3eae35cf10cc427cd85b264da"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 14:05:23 GMT

{
  "change_date": "2020-12-24T14:02:40.897605",
  "person_id": "2",
  "person_name": "Wim - update 1"
}
```
Perform the second update again but now with the recent `ETag` in the `If-Match` request header:
```bash
$ curl --request PUT --include \
   localhost:5000/persons/2 \
   --data '{"person_name": "Wim - update 2"}' \
   --header "If-Match:b90595e3eae35cf10cc427cd85b264da"
```
Results in a status code `200` now. 
Resource correctly updated for the second time, new `ETag` available in response header:
```bash
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 107
ETag: "3e2b0cb26be62a4287c33054f51a1974"
Server: Werkzeug/1.0.1 Python/3.9.1
Date: Thu, 24 Dec 2020 14:09:19 GMT

{
  "change_date": "2020-12-24T14:09:19.086225",
  "person_id": "2",
  "person_name": "Wim - update 2"
}
```
