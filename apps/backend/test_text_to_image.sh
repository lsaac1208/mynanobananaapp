#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1OTMwNDEzOSwianRpIjoiYjA1ZWM0ZDktYTE0NC00Zjc5LWFlNDItZWY1YjE2YmIyY2I1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNzU5MzA0MTM5LCJjc3JmIjoiZmVjYWE0NjYtYmY4Ni00MmM0LTkxZGYtOWI3ZmM4MGMxZjdmIiwiZXhwIjoxNzU5MzExMzM5fQ.zwuzzCkTcK-xRgCcm5UXzDOeHYxAaRhbrR33NxV_3nA"

echo "Testing text-to-image API..."

curl -X POST http://localhost:5000/api/generate/text-to-image \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "a cute orange cat",
    "model": "nano-banana",
    "size": "1x1",
    "n": 1
  }' 2>&1
