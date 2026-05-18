import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_subscription_info",
            "description": "Get details about a specific subscription",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the subscription (e.g., Netflix, Spotify)"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_subscriptions",
            "description": "Get a list of all active subscriptions",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_monthly_spend",
            "description": "Calculate total monthly spending across all subscriptions",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_subscriptions_by_category",
            "description": "Find all subscriptions in a specific category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category (entertainment, productivity, health, etc.)"
                    }
                },
                "required": ["category"]
            }
        }
    }
]

# Load subscription data
def load_subscriptions():
    """Load subscriptions from JSON file"""
    try:
        with open("my_subscriptions.json", "r") as f:
            subs = json.load(f)
            # Convert to dict for easier lookup
            return {sub["name"].lower(): sub for sub in subs}
    except FileNotFoundError:
        print("⚠️  my_subscriptions.json not found. Create it first.")
        return {}

VENDOR_DB = load_subscriptions()

# Function implementations
def get_subscription_info(name):
    """Get info about a specific subscription"""
    sub = VENDOR_DB.get(name.lower())
    if sub:
        return sub
    else:
        return {"error": f"Subscription '{name}' not found"}

def list_all_subscriptions():
    """List all subscriptions"""
    if not VENDOR_DB:
        return {"error": "No subscriptions found"}
    
    return {
        "total_subscriptions": len(VENDOR_DB),
        "subscriptions": [
            f"{sub['name']}: ${sub['monthly_cost']}/month"
            for sub in VENDOR_DB.values()
        ]
    }

def calculate_total_monthly_spend():
    """Calculate total monthly spend"""
    if not VENDOR_DB:
        return {"error": "No subscriptions found"}
    
    total = sum(sub["monthly_cost"] for sub in VENDOR_DB.values())
    return {
        "total_monthly": total,
        "total_annual": total * 12,
        "average_per_subscription": total / len(VENDOR_DB)
    }

def find_subscriptions_by_category(category):
    """Find subscriptions in a category"""
    matches = [
        sub for sub in VENDOR_DB.values()
        if sub.get("category", "").lower() == category.lower()
    ]
    
    if not matches:
        return {"error": f"No subscriptions found in category '{category}'"}
    
    total = sum(sub["monthly_cost"] for sub in matches)
    return {
        "category": category,
        "count": len(matches),
        "subscriptions": [sub["name"] for sub in matches],
        "total_monthly_spend": total
    }

def run_agent(user_message):
    """Run the agent with tool use"""
    print(f"\n{'='*60}")
    print(f"USER: {user_message}")
    print(f"{'='*60}\n")
    
    messages = [{"role": "user", "content": user_message}]
    
    # Loop to handle multiple tool calls
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if GPT wants to use a tool
        if response_message.tool_calls:
            # Add GPT's response to messages
            messages.append(response_message)
            
            # Process each tool call
            for tool_call in response_message.tool_calls:
                print(f"\n🔧 GPT called: {tool_call.function.name}")
                print(f"   With input: {tool_call.function.arguments}")
                
                # Parse arguments
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                function_name = tool_call.function.name
                
                if function_name == "get_subscription_info":
                    tool_result = get_subscription_info(function_args.get("name", ""))
                elif function_name == "list_all_subscriptions":
                    tool_result = list_all_subscriptions()
                elif function_name == "calculate_total_monthly_spend":
                    tool_result = calculate_total_monthly_spend()
                elif function_name == "find_subscriptions_by_category":
                    tool_result = find_subscriptions_by_category(function_args.get("category", ""))
                else:
                    tool_result = {"error": "Unknown function"}
                
                print(f"\n📊 Function returned: {json.dumps(tool_result, indent=2)}")
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result)
                })
            
            # Continue the loop
            continue
        
        else:
            # GPT is done
            print(f"\n💬 GPT: {response_message.content}\n")
            print(f"💰 Total tokens used: {response.usage.total_tokens}")
            print(f"🔄 Tool iterations: {iteration}")
            return response_message.content
    
    # Max iterations reached
    print(f"\n⚠️  Hit max iterations ({max_iterations})")
    return "Agent exceeded maximum tool calls"


# Test cases
if __name__ == "__main__":
    # Real questions about YOUR subscriptions
    run_agent("What am I spending on subscriptions each month?")
    run_agent("Show me all my entertainment subscriptions")
    run_agent("When does my Netflix renew?")
    run_agent("How much am I spending annually on all this?")
    run_agent("What subscriptions do I have?")