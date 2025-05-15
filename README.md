# areq

[![PyPI version](https://badge.fury.io/py/areq.svg)](https://badge.fury.io/py/areq)
[![Python Versions](https://img.shields.io/pypi/pyversions/areq.svg)](https://pypi.org/project/areq/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

areq is an asynchronous drop-in replacement for the popular `requests` library. It provides the same familiar API as `requests` but with async/await support, making it perfect for modern Python applications that need to make HTTP requests efficiently.

## Features

- 🚀 **Async by Default**: Built on top of `httpx` for modern async/await support
- 🔄 **Drop-in Replacement**: Compatible with `requests` API, making migration easy
- 🛠 **Type Hints**: Full type support for better IDE integration and code safety
- 📦 **Lightweight**: Minimal dependencies, just `httpx` and `requests`

## Installation

```bash
pip install areq
```

## Quick Start

```python
import areq

# Async GET request
async def fetch_data():
    response = await areq.get("https://api.example.com/data")
    return response.json()

# Async POST request with JSON
async def create_item():
    data = {"name": "example", "value": 123}
    response = await areq.post("https://api.example.com/items", json=data)
    return response.json()
```

## API Reference

areq provides the same methods as `requests`:

- `areq.get(url, **kwargs)`
- `areq.post(url, **kwargs)`
- `areq.put(url, **kwargs)`
- `areq.delete(url, **kwargs)`
- `areq.head(url, **kwargs)`
- `areq.options(url, **kwargs)`
- `areq.patch(url, **kwargs)`
- `areq.request(method, url, **kwargs)`

All methods are async and return an `areq.AreqResponse` object, which is compatible with `requests.Response`.

### Response Object

The response object provides the same interface as `requests.Response`:

```python
response = await areq.get("https://api.example.com/data")

# Access response data
print(response.status_code)  # HTTP status code
print(response.headers)      # Response headers
print(response.text)         # Response body as text
print(response.json())       # Parse JSON response
print(response.content)      # Raw response content
```

## Advanced Usage

### Custom Headers

```python
headers = {"Authorization": "Bearer token123"}
response = await areq.get("https://api.example.com/data", headers=headers)
```

### Query Parameters

```python
params = {"page": 1, "limit": 10}
response = await areq.get("https://api.example.com/items", params=params)
```

### File Upload

```python
files = {"file": open("document.pdf", "rb")}
response = await areq.post("https://api.example.com/upload", files=files)
```

### Timeout

```python
response = await areq.get("https://api.example.com/data", timeout=5.0)
```

## Migration from requests

If you're using `requests`, migrating to `areq` is straightforward:

```python
# Before (requests)
import requests
response = requests.get("https://api.example.com/data")
data = response.json()

# After (areq)
import areq
async def get_data():
    response = await areq.get("https://api.example.com/data")
    data = response.json()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Ganesh Palanikumar - [@ganeshpkumar93](https://github.com/ganeshpkumar93)