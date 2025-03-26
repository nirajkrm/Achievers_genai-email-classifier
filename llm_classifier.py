# llm_classifier.py

import openai
import json
from config import OPENAI_API_KEY, OPENAI_MODEL, SUBJECT_RULES

# Initialize OpenAI client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

def rule_based_classification(subject, body):
    """
    Enhanced rule-based classifier with better alignment to observed outputs
    """
    text = f"{subject} {body}".lower()
    result = {
        "primary_request": {
            "request_type": "Others",
            "sub_request_type": "Others",
            "primary_intent": "No matching rule detected",
            "priority": "Medium",
            "confidence": 60,
            "reasoning": "Fallback to default classification"
        },
        "secondary_requests": []
    }

    # Enhanced keyword matching with priority detection
    for rule_name, rule in SUBJECT_RULES.items():
        keywords = rule.get("keywords", [])
        if any(kw.lower() in text for kw in keywords):
            priority = "High" if any(pkw in text for pkw in ["urgent", "immediate", "due"]) else rule.get("priority", "Medium")
            
            result["primary_request"] = {
                "request_type": rule.get("request_type", "Others"),
                "sub_request_type": rule.get("sub_request_type", "Others"),
                "primary_intent": f"Identified via rule: {rule_name}",
                "priority": priority,
                "confidence": 75,  # Higher confidence for rule-based matches
                "reasoning": f"Matched keywords: {', '.join(keywords)}"
            }
            break
            
    return result

async def classify_email(subject, body):
    """
    Optimized classifier based on observed output patterns
    """
    prompt = f"""**Financial Email Classification Task**

Analyze this loan servicing email and provide:

1. PRIMARY REQUEST:
- request_type: Broad category (e.g., "Loan Repayment", "Fee Payment")
- sub_request_type: Specific action (e.g., "Principal Payment", "Amendment Fee")
- primary_intent: 1-sentence summary of the main action requested
- priority: "High"/"Medium"/"Low" based on urgency
- confidence: 1-100% certainty
- reasoning: Brief justification for classification

2. SECONDARY REQUESTS: Only if clearly distinct additional actions

**Output Format (STRICT JSON):**
{{
  "primary_request": {{
    "request_type": "[Standard Category]",
    "sub_request_type": "[Specific Action]", 
    "primary_intent": "[Summary]",
    "priority": "High/Medium/Low",
    "confidence": 0-100,
    "reasoning": "[Logical Explanation]"
  }},
  "secondary_requests": []
}}

**Email to Classify:**
Subject: {subject}
Body:
{body}
"""

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a senior loan servicing analyst. "
                        "Classify emails with precision using standard financial categories. "
                        "Focus on the primary actionable request. "
                        "Secondary requests should only be included for truly separate actions."
                    )
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.1,  # Lower temperature for more consistent outputs
            response_format={"type": "json_object"},
            max_tokens=400
        )
        
        data = json.loads(response.choices[0].message.content)
        
        # ===== VALIDATION & NORMALIZATION =====
        REQUIRED_FIELDS = [
            "request_type", 
            "sub_request_type", 
            "primary_intent",
            "priority", 
            "confidence", 
            "reasoning"
        ]
        
        # Validate primary request
        if not all(field in data["primary_request"] for field in REQUIRED_FIELDS):
            raise ValueError("Primary request missing required fields")
            
        # Normalize priorities
        data["primary_request"]["priority"] = (
            "High" if "high" in data["primary_request"]["priority"].lower() 
            else "Low" if "low" in data["primary_request"]["priority"].lower() 
            else "Medium"
        )
        
        # Ensure confidence is numeric
        try:
            data["primary_request"]["confidence"] = min(100, max(0, int(data["primary_request"]["confidence"])))
        except (ValueError, TypeError):
            data["primary_request"]["confidence"] = 80  # Default
            
        # Ensure secondary_requests exists and is list
        if "secondary_requests" not in data or not isinstance(data["secondary_requests"], list):
            data["secondary_requests"] = []
            
        return data
        
    except Exception as e:
        print(f"LLM Classification Error: {str(e)}")
        return rule_based_classification(subject, body)