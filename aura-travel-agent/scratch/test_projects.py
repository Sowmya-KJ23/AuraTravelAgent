import os
from google import genai
from google.genai import errors

projects = [
    "agenticai-2026",
    "devknowledgetest",
    "gen-lang-client-0277594550",
    "perfect-axe-w18qq",
    "project-1a233833-b2d6-4b26-9ba",
    "project-53f2f1c1-16a9-4cd5-a75",
    "project-54d50c1c-cd7a-430d-96f",
    "project-7ce363f7-af5e-4e73-aa6",
    "project-a109056d-7ad1-4558-bea",
    "project-d9e26613-c504-4d0d-8f9",
    "project-dc7de1e8-06af-480e-a2c",
    "project-f7d201ea-8546-4c7d-b4c",
    "project-ff5a5163-81d1-4781-8eb"
]

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Clear API key variables to force Vertex AI / ADC
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]

for proj in projects:
    print(f"Testing project: {proj}...", end="", flush=True)
    os.environ["GOOGLE_CLOUD_PROJECT"] = proj
    try:
        client = genai.Client(vertexai=True, project=proj, location="us-central1")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="test"
        )
        print(" SUCCESS!")
        print(f"Result: {response.text}")
    except errors.ClientError as e:
        if "BILLING_DISABLED" in str(e) or "billing" in str(e).lower():
            print(" FAILED (Billing disabled)")
        else:
            print(f" FAILED (ClientError: {e})")
    except Exception as e:
        print(f" FAILED (Unexpected error: {type(e).__name__}: {e})")
