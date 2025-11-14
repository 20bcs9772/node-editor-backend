# Node Editor Backend

A backend service built using **FastAPI** that parses and validates pipeline graphs (nodes + edges).
It checks node/edge counts, validates Directed Acyclic Graphs (DAG), and provides detailed pipeline analytics.

---

## Installation

Make sure you have **Python 3.9+** installed.

### Clone the repository

```bash
git clone https://github.com/20bcs9772/node-editor-backend.git
cd node-editor-backend
```

### Install dependencies

All required packages are listed in **requirements.txt**.

```bash
pip install -r requirements.txt
```

---

## Running the Server

Start the FastAPI server using:

```bash
uvicorn main:app --reload
```

This will run the API at:

```
http://127.0.0.1:8000
```

---

## What This Backend Does

### ✔ Parse pipeline JSON

### ✔ Count nodes and edges

### ✔ Check if the graph is a **DAG** (Directed Acyclic Graph)

### ✔ Detect cycles using DFS

### ✔ Provide extended analytics (node types, source/sink nodes)

---

## API Endpoints

### **GET /**

Ping endpoint to test server availability.

**Response:**

```json
{
  "Ping": "Pong"
}
```

---

### **POST /pipelines/parse**

Parses pipeline JSON and returns:

* `num_nodes`
* `num_edges`
* `is_dag` (boolean)

#### **Form Data**

| Key      | Type   | Description                                |
| -------- | ------ | ------------------------------------------ |
| pipeline | string | JSON string containing `nodes` and `edges` |

#### **Example Response**

```json
{
  "num_nodes": 5,
  "num_edges": 4,
  "is_dag": true
}
```

---

### **POST /pipelines/validate**

Provides extended validation details:

* Node & edge count
* DAG check
* Node type distribution
* Source nodes
* Sink nodes

#### **Example Response**

```json
{
  "num_nodes": 5,
  "num_edges": 4,
  "is_dag": true,
  "node_types": { 
    "Text": 2,
    "Input": 3
  },
  "source_nodes": ["node_1"],
  "sink_nodes": ["node_5"]
}
```

---

## Input Format Example

The API expects pipeline JSON like:

```json
{
  "nodes": [
    {
      "id": "1",
      "type": "Input",
      "position": { "x": 100, "y": 200 },
      "data": {},
      "width": 180,
      "height": 80
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "1",
      "sourceHandle": "1-out",
      "target": "2",
      "targetHandle": "2-in",
      "type": "smoothstep"
    }
  ]
}
```

Send it as a **string** inside form-data.

---

## Testing with cURL

```bash
curl -X POST http://127.0.0.1:8000/pipelines/parse \
  -F 'pipeline={"nodes": [], "edges": []}'
```

---

## Notes

* CORS is fully open (`allow_origins=["*"]`).
* Uses Pydantic for validation.
* DAG detection uses DFS with 3-state coloring (WHITE, GRAY, BLACK).
* Designed for connecting with frontend node-based editors (e.g., React Flow).
