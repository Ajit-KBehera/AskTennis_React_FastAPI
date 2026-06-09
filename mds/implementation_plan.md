# Shift to Vertex AI for Google Cloud $300 Free Credits

This plan details how to add support for routing GenAI requests through Google Cloud's enterprise AI platform, **Vertex AI**, utilizing your $300 free trial credits pool. 

We will modify the backend to support both **Google AI Studio (Google GenAI API)** and **Google Cloud Vertex AI** side-by-side:
- If `GCP_PROJECT_ID` is set in the environment, the application will use `ChatVertexAI` (Vertex AI SDK) and bypass Google API key validation.
- If `GCP_PROJECT_ID` is not set, the application will fall back to using `ChatGoogleGenerativeAI` (AI Studio SDK) and require `GOOGLE_API_KEY`.

---

## User Review Required

> [!IMPORTANT]
> **1. Install the langchain-google-vertexai package**
> Due to sandboxing limitations of the agent environment, you must run the dependency installation command on your local terminal after approving this plan:
> ```bash
> # Run this command in your terminal:
> .venv/bin/pip install langchain-google-vertexai
> ```
> We will update `requirements.txt` to include this package permanently.

I HAVE DONE IT AND INSTALLED IT ALREADY

> [!NOTE]
> **2. Environment Variables Configuration**
> You will need to add your Google Cloud project configuration to your backend `.env` file:
> ```env
> GCP_PROJECT_ID="your-gcp-project-id"  # Set to your GCP project ID to enable Vertex AI
> GCP_LOCATION="us-central1"           # Optional: defaults to us-central1
> DEFAULT_MODEL="gemini-1.5-flash"      # Optional: Vertex AI supported model (e.g. gemini-1.5-flash)
> ```

I HAVE UPDATED .env FILE CHECK

> [!IMPORTANT]
> **3. Local GCP Authentication**
> Since Vertex AI uses your GCP project authentication, ensure you have authenticated locally:
> ```bash
> gcloud auth application-default login
> ```
> Alternatively, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in your `.env` pointing to a service account JSON credentials file.



---

## Proposed Changes

### Configuration Layer

#### [MODIFY] [config.py](file:///Users/ajitbehera/Codes/AskTennis_React_FastAPI/backend/app/core/config/config.py)
- Load `GCP_PROJECT_ID` and `GCP_LOCATION` from environment variables.
- Update `_get_api_key` and `validate_config` to bypass the `GOOGLE_API_KEY` requirement when `GCP_PROJECT_ID` is configured.

#### [MODIFY] [.env.example](file:///Users/ajitbehera/Codes/AskTennis_React_FastAPI/backend/.env.example)
- Add sections for `GCP_PROJECT_ID` and `GCP_LOCATION` under optional/Vertex AI configurations.

---

### LLM Integration Layer

#### [MODIFY] [llm_setup.py](file:///Users/ajitbehera/Codes/AskTennis_React_FastAPI/backend/app/infrastructure/llm/llm_setup.py)
- Import `ChatVertexAI` conditionally from `langchain_google_vertexai`.
- Update `LLMFactory.setup_llm_components` and `LLMFactory.create_llm` to accept `gcp_project_id` and `gcp_location`.
- Conditionally return `ChatVertexAI` if `gcp_project_id` is passed, otherwise return `ChatGoogleGenerativeAI`.
- Relax type annotations to accept a Union of both chat model classes or general langchain BaseChatModel.

---

### Agent Factory Layer

#### [MODIFY] [agent_factory.py](file:///Users/ajitbehera/Codes/AskTennis_React_FastAPI/backend/app/domain/agent/agent_factory.py)
- Pass `config.gcp_project_id` and `config.gcp_location` from the configuration class into `LLMFactory.setup_llm_components`.

---

### Dependencies

#### [MODIFY] [requirements.txt](file:///Users/ajitbehera/Codes/AskTennis_React_FastAPI/backend/requirements.txt)
- Add `langchain-google-vertexai>=2.0.0` to the AI/LLM Framework section.

---

## Verification Plan

### Manual Verification
1. Approve this implementation plan.
2. Run `pip install langchain-google-vertexai` in your virtual environment.
3. Configure `GCP_PROJECT_ID` in `.env` and verify that the backend starts up successfully with Vertex AI.
4. Interact with the chat interface to verify that model responses work seamlessly through Vertex AI.
5. Temporarily comment out `GCP_PROJECT_ID` in `.env` to verify that the application falls back to AI Studio (using `GOOGLE_API_KEY`) and continues working as expected.
