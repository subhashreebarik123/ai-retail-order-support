\# AI-Powered Retail Order Support Assistant



A backend application that helps retail customers get order information and answers to common customer support questions using a database and Generative AI.



\## Features



\- Retrieve order details using an order ID.

\- Answer order-related questions using live database records.

\- Generate AI responses to general retail support questions using Google Gemini.

\- Validate requests and handle missing or unknown orders.

\- Expose REST APIs through FastAPI.

\- Store order information in MySQL.

\- Run MySQL in Docker.

\- Automatically test API behavior using pytest and mocked AI responses.

\- Interactive API documentation using Swagger UI.



\## Technology Stack



\- \*\*Language:\*\* Python 3.13

\- \*\*Backend Framework:\*\* FastAPI

\- \*\*Generative AI:\*\* Google Gemini API

\- \*\*Database:\*\* MySQL 8.4

\- \*\*ORM:\*\* SQLAlchemy

\- \*\*Containerization:\*\* Docker

\- \*\*Testing:\*\* pytest, FastAPI TestClient, unittest.mock

\- \*\*API Documentation:\*\* Swagger UI



\## Architecture



```text

Customer

&#x20;  |

&#x20;  v

FastAPI REST API

&#x20;  |

&#x20;  v

Chat and Order Lookup Logic

&#x20;  |

&#x20;  +--------------------+

&#x20;  |                    |

&#x20;  v                    v

MySQL Database      Google Gemini

&#x20;  |                    |

&#x20;  v                    v

Order Details       AI-generated Answers

&#x20;  |                    |

&#x20;  +----------+---------+

&#x20;             |

&#x20;             v

&#x20;      Customer Response

```



Order-specific questions containing an order ID are answered using database records. General retail questions are sent to Gemini with customer-support instructions.



\## API Endpoints



| Method | Endpoint | Purpose |

|--------|----------|---------|

| GET | `/` | Welcome message |

| GET | `/health` | Health check |

| GET | `/orders/{order\_id}` | Retrieve order details |

| POST | `/chat` | Answer customer questions |



\## Sample API Requests



\### Get order details



```http

GET /orders/ORD1001

```



Example response:



```json

{

&#x20; "order\_id": "ORD1001",

&#x20; "customer\_name": "Customer A",

&#x20; "status": "Shipped",

&#x20; "estimated\_delivery": "2026-10-29"

}

```



\### Ask a customer support question



```http

POST /chat

Content-Type: application/json

```



Request:



```json

{

&#x20; "question": "What is the status of my order ORD1002?"

}

```



Example response:



```json

{

&#x20; "answer": "Order ID: ORD1002. Status: Processing. Estimated delivery: 2026-10-31."

}

```



\## Local Setup



\### Prerequisites



\- Python 3.13

\- Docker Desktop

\- A Google Gemini API key



\### 1. Clone the repository



```bash

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd ai-retail-order-support

```



\### 2. Create a virtual environment



```powershell

python -m venv .venv

```



\### 3. Install dependencies



```powershell

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file in the project root:



```env

GEMINI\_API\_KEY=your\_gemini\_api\_key

MYSQL\_HOST=127.0.0.1

MYSQL\_PORT=3306

MYSQL\_USER=root

MYSQL\_PASSWORD=your\_local\_mysql\_password

MYSQL\_DATABASE=retail\_support

```



Use your own local MySQL credentials. Never commit `.env` or API keys to GitHub.



\### 5. Start the MySQL container



Start the existing configured container if it already exists:



```powershell

docker start ai-retail-mysql

```



If setting up a new environment, configure MySQL and create the `retail\_support` database and `orders` table before starting the application.



\### 6. Start the API



```powershell

.\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --port 8000

```



\### 7. Open Swagger UI



Visit:



http://127.0.0.1:8000/docs



\## Run Automated Tests



```powershell

.\\.venv\\Scripts\\python.exe -m pytest -v

```



The current test suite contains eight passing tests covering health checks, order retrieval, chat behavior, input validation, and mocked Gemini responses.



\## Security Notes



\- Store API keys and passwords in environment variables.

\- Never commit secrets or production credentials.

\- Use appropriate database permissions and authentication in production.

\- Add authentication, authorization, rate limiting, and monitoring before production deployment.



\## Future Enhancements



\- Add a web-based customer chat interface.

\- Implement order status and delivery notifications.

\- Add retrieval-augmented generation (RAG) for verified retail policies.

\- Containerize the FastAPI application.

\- Add CI/CD with automated testing and deployment.

\- Add monitoring, logging, and production security controls.



\## Disclaimer



This is a learning and portfolio project using sample retail order data. It is not connected to a real retailer or live shipping provider.

