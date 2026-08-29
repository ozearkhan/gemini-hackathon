"""
org Hackathon — Demo ADK Agent
================================
Reference example for Stream 2 participants.

This agent can be deployed to:
  - Cloud Run with A2A:     adk deploy cloud_run demo_agent --a2a ...
  - Vertex AI Agent Engine: adk deploy agent_engine demo_agent ...

The root_agent variable is the ADK entry point — it MUST be named 'root_agent'.
"""

from google.adk.agents import Agent

# ─── Tool definitions ──────────────────────────────────────────────────────────
# Add your custom tools here as Python functions decorated with @tool.
# Example:
#   from google.adk.tools import tool
#   @tool
#   def get_ticket_status(ticket_id: str) -> dict:
#       """Look up a ServiceNow ticket by ID."""
#       ...


# ─── Root Agent ────────────────────────────────────────────────────────────────
# This is the main agent entry point. ADK looks for a variable named root_agent.
root_agent = Agent(
    name="org_hackathon_assistant",
    model="gemini-2.5-flash",
    description=(
        "org Hackathon Demo Agent — an AI assistant showcasing Google Gemini "
        "Enterprise capabilities at the org hackathon."
    ),
    instruction="""You are the org Hackathon Demo Agent, an AI assistant showcasing 
Google Gemini Enterprise capabilities at the org hackathon.

Your role:
- Welcome participants and explain what Gemini Enterprise can do
- Answer questions about the hackathon format (Stream 1: Low-Code, Stream 2: High-Code)
- Describe integration possibilities with Microsoft 365, ServiceNow, and Salesforce
- Explain the two deployment patterns: Cloud Run (A2A) and Vertex AI Agent Engine

Key information:
- Hackathon portal: https://epa.ms/gemini-enterprise (use Chrome)
- Stream 1: Low-code agents using Gemini Enterprise App builder (no coding required)
- Stream 2: Custom ADK agents deployed to Cloud Run or Vertex AI Agent Engine
- Evaluation criteria: Business Impact 30%, Technical Extensibility 30%, UX 20%, Presentation 20%

Always be encouraging, enthusiastic, and helpful. If asked technical questions beyond 
your knowledge, direct participants to the mentors or the Participant Knowledge Base.
""",
    # tools=[get_ticket_status],  # Uncomment and add your tools here
)
