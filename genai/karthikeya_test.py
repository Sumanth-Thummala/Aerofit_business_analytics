import sys
import boto3, time, json, os


# Get the directory of the current file (main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the JSON file
file_path = os.path.join(current_dir, "openapi.json")

# Open and read the JSON file
with open(file_path, "r") as file:
    open_api_specifications = json.load(file)


def generate_response_from_LLM(
    messages, user_message, temperature=0.0, top_p=0.1, max_tokens=4096
):
    bedrockClient = boto3.client(
        service_name="bedrock-runtime", region_name="us-west-2"
    )
    modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    print("Invoking the Claude for Connect JS code")

    response = bedrockClient.invoke_model(
        modelId=modelId,
        body=json.dumps(
            {
                "system": system_message,
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "messages": messages,
            }
        ),
    )

    assistant_response = json.loads(response.get("body").read())["content"][0]["text"]
    assistant_response = assistant_response.replace("\\", "")

    return assistant_response


delimiter = "#####"

steps_to_follow_to_understand_openapi_specifications = """
Each API details is mentioned in the below format.
format: {
        "method": "get",
        "path": "/api/v2/users",
        "operationId": "GetAllUsers",
        "description": "This endpoint retrieves all users for the current organization. <br><br>For Global Admin Tool Organizations, if the `X-Degreed-Organization-Code` header is included, the endpoint will return users for the Tenant Organization related to the header value as long as the organization is a member of the Global Admin Tool Organization. <h3>Required Scope</h3>`users:read` or `users:write`",
        "summary": "Get All Users"
    }
    
- "method" attribute tells which type of HTTP method is used to call the API.
- "path" attribute indicates the API path.
- "operationId" attribute is used to uniquely identify an API.
- "description" attribute tell you about the API usage and functionality in detail. You can use this details to generate the plan
- "summary" attribute provides you the short description of the API. You can use this attribute along with "description" attribute to generate the plan. 
"""

system_message = f"""
You are a customer service assistant, that generates a detailed, step by step plan to resolve customer queries by breaking down the customer query into smaller precise sub tasks based on the apo documentation provided.
Respond in a very helpful and a friendly tone with very concise answers.

You will be provided with the openAPI specification in the following format:
openAPI specifications: {open_api_specifications}

Follow below steps to understand API specification: {steps_to_follow_to_understand_openapi_specifications}

Output the generated plan in a plain text format as an ordered list.
Do not output any additional text that is not part of the plan.
Always use noun to specify the resources, the API's.

You will be provided with customer queries.
The customer query will be delimited with {delimiter} characters.

Strictly Follow the below steps to answer the customer queries. 

Step 1. First decide whether the user is asking for any specific resources or not.
Step 2. If the user is asking about some specific resources, identify whether all those resources are in the openAPI specifications or not.
Step 3. If even a SINGLE ONE of those resources, the user has asked for is NOT present in the openAPI specification, inform the user that the resource is not available in the document, would the user like to generate the plan without the missing resource. DO NOT GENERATE THE PLAN in this case. 
Step 4. If all the resources are found then only generate the plan.
Step 5. If the user responses is in affirmative sentiment, then you need to generate the plan otherwise ask the user is there anything else you can help the user with.
"""

few_shot_user_1 = """
Generate a plan to retrieve paginated Employees along with their Department and location details.
"""

few_shot_assistant_1 = """
1: Connect to the API and authenticate our request.
2: Make an API call to get All Employees.
3: If there is no API to fetch paginated Employees, write a JS Code to slice the Employees retrieved from step 2.
4: Write JS code to iterate over each Employee returned from step 2 and do the following:
    a. Make an API call to get each Employee's Department details.
    b. Make an API call to get each Employee's location details.
5: Write JS code to combine the Employee data with their respective Department and location details.
6: Write JS code to compile all the gathered information into a structured format, creating a final array of Employee objects with their respective Department and location details.
7: Write JS code to output the final structured data by logging it to the console.
"""

few_shot_user_2 = """
Generate a plan to retrieve paginated Employees along with their Department and title details.
"""

few_shot_assistant_2 = """
I won't be able to generate a plan to get all the Employees along with their titles because there is no resources called title, mentioned in the openAPI specifications. Do you want me to generate a plan without title?
"""

user_message = """Generate a plan to get paginated Users and for each fetch their Groups, Completions, Titles, Certificates."""

messages = [
    {
        "role": "user",
        "content": f"{delimiter}{few_shot_user_1}{delimiter}",
    },
    {
        "role": "assistant",
        "content": f"{delimiter}{few_shot_assistant_1}{delimiter}",
    },
    {
        "role": "user",
        "content": f"{delimiter}{few_shot_user_2}{delimiter}",
    },
    {
        "role": "assistant",
        "content": f"{delimiter}{few_shot_assistant_2}{delimiter}",
    },
    {"role": "user", "content": f"{delimiter}{user_message}{delimiter}"},
]

start_time = time.time()
assistant_response = generate_response_from_LLM(messages, user_message)
end_time = time.time()

print(assistant_response)
print(f"time taken to generate code: {end_time-start_time} seconds")