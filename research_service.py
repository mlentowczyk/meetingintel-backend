"""
Research Service - Claude researches attendees and generates meeting briefs
This is where I (Claude) do all the work
"""

import anthropic
import os
from datetime import datetime
from typing import List, Dict

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

async def generate_meeting_brief(
    meeting_title: str,
    meeting_time: str,
    attendees: List[Dict[str, str]]
) -> Dict:
    """
    Generate comprehensive meeting brief using Claude + web search
    
    I research each attendee and generate actionable insights
    """
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Build attendee list for prompt
    attendee_info = "\n".join([
        f"- {a['name']} ({a['email']})"
        for a in attendees
    ])
    
    # Research prompt
    prompt = f"""You are a professional meeting preparation assistant. Generate a comprehensive brief for this upcoming meeting:

**Meeting Details:**
- Title: {meeting_title}
- Time: {meeting_time}
- Attendees:
{attendee_info}

**Your Task:**
1. Research each attendee (use web search to find their LinkedIn, recent activity, background)
2. Research the companies they work for (extract domain from email)
3. Generate actionable meeting insights

**Important Guidelines:**
- Focus on ACTIONABLE intelligence (not just facts)
- Provide conversation starters that show you did your homework
- Suggest questions that demonstrate genuine interest
- Be professional but personable

**Output Format (JSON):**
{{
    "attendees": [
        {{
            "name": "...",
            "email": "...",
            "role": "...",
            "company": "...",
            "background": "Brief 2-3 sentence summary",
            "recent_activity": "What they've been posting/doing recently",
            "key_fact": "One interesting fact to mention"
        }}
    ],
    "conversation_starters": [
        "Specific, personalized conversation starter that references their work/interests",
        "Another one...",
        "..."
    ],
    "questions_to_ask": [
        "Thoughtful question about their work",
        "Another...",
        "..."
    ],
    "strategy": "2-3 sentence meeting strategy (what to emphasize, how to position yourself, key themes)",
    "generated_at": "{datetime.now().isoformat()}"
}}

Use web search to find current, accurate information. Be thorough but concise.
"""

    # Call Claude with web search enabled
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search"
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract response
        brief_text = ""
        for block in response.content:
            if block.type == "text":
                brief_text += block.text
        
        # Parse JSON response
        import json
        
        # Claude might wrap in ```json blocks
        if "```json" in brief_text:
            json_start = brief_text.find("```json") + 7
            json_end = brief_text.find("```", json_start)
            json_text = brief_text[json_start:json_end].strip()
        elif "```" in brief_text:
            json_start = brief_text.find("```") + 3
            json_end = brief_text.find("```", json_start)
            json_text = brief_text[json_start:json_end].strip()
        else:
            json_text = brief_text.strip()
        
        brief_data = json.loads(json_text)
        return brief_data
        
    except Exception as e:
        print(f"Error generating brief: {e}")
        # Return fallback brief if API fails
        return generate_fallback_brief(attendees)


def generate_fallback_brief(attendees: List[Dict[str, str]]) -> Dict:
    """
    Generate basic brief if API call fails
    """
    return {
        "attendees": [
            {
                "name": a["name"],
                "email": a["email"],
                "role": "Role not yet researched",
                "company": extract_company_from_email(a["email"]),
                "background": "Research in progress...",
                "recent_activity": "",
                "key_fact": ""
            }
            for a in attendees
        ],
        "conversation_starters": [
            "Thank you for taking the time to meet today",
            f"I'm excited to learn more about {extract_company_from_email(attendees[0]['email'])}",
            "What are your top priorities for this quarter?"
        ],
        "questions_to_ask": [
            "What challenges are you currently facing?",
            "What does success look like for you?",
            "How can we best support your goals?"
        ],
        "strategy": "Focus on building rapport, understanding their needs, and exploring potential collaboration opportunities.",
        "generated_at": datetime.now().isoformat()
    }


def extract_company_from_email(email: str) -> str:
    """
    Extract company name from email domain
    """
    try:
        domain = email.split("@")[1]
        company = domain.split(".")[0]
        return company.capitalize()
    except:
        return "Company"


# For testing without API key
async def generate_mock_brief(attendees: List[Dict[str, str]]) -> Dict:
    """
    Mock brief for testing
    """
    return {
        "attendees": [
            {
                "name": attendees[0]["name"],
                "email": attendees[0]["email"],
                "role": "VP of Sales",
                "company": "Acme Corp",
                "background": "10+ years in B2B SaaS sales. Previously led sales at Salesforce for the mid-market segment. Passionate about AI adoption in sales processes.",
                "recent_activity": "Recently posted on LinkedIn about their Q4 results and 2025 strategy",
                "key_fact": "Just completed Stanford Executive Program in AI for Business"
            }
        ],
        "conversation_starters": [
            "I saw your recent post about Q4 results - congratulations on the strong finish! How are you thinking about building on that momentum?",
            "I noticed you completed the Stanford AI program - I'm curious how you're applying those insights to your sales strategy",
            "Your approach to the mid-market segment at Salesforce is really interesting. What lessons are you bringing to Acme?"
        ],
        "questions_to_ask": [
            "What are your top 3 priorities for Q1 2025?",
            "How do you see AI transforming your sales process over the next year?",
            "What challenges are you facing in scaling your sales team?",
            "How do you typically evaluate new tools or partners?"
        ],
        "strategy": "Position as a partner who understands their growth trajectory and can provide ROI-focused solutions. Emphasize speed to value and how you've helped similar companies scale. Ask about their decision timeline and key stakeholders early in the conversation.",
        "generated_at": datetime.now().isoformat()
    }
