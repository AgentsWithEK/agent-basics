from litellm import completion
import asyncio
import json
import time


class Agent:
    system_prompt: str
    schemas: list[dict]
    messages: list[dir] = list()
    functions: dict

    def __init__(self, system_prompt: str, schemas: list, functions: dict = None):
        self.system_prompt = system_prompt
        self.schemas = schemas
        self.functions = functions or {}

    async def invoke(self, user_query: str):
        start_time = time.time()

        if not self.messages:
            self.messages.append(
                {"role": "system", "content": self.system_prompt},
            )

        self.messages.append(
            {"role": "user", "content": user_query},
        )

        while True:
            response = completion(
                model="anthropic/claude-sonnet-4-20250514",
                messages=self.messages,
                tools=self.schemas,
            )

            # Check if the model wants to call a tool
            response_message = response.choices[0].message

            # If no tool calls, return the response
            if (
                not hasattr(response_message, "tool_calls")
                or not response_message.tool_calls
            ):
                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"\n{'=' * 60}")
                print(f"Total Time: {elapsed_time:.2f}s")
                print(f"{'=' * 60}\n")

                return response_message.content

            # Add assistant's response to messages
            self.messages.append(response_message)

            # Print all tool calls first
            for idx, tool_call in enumerate(response_message.tool_calls, 1):
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                args_str = ", ".join([f'{k}="{v}"' for k, v in function_args.items()])
                print(f"\nTool {idx}: {function_name}({args_str})")

            # Execute all tool calls in parallel
            async def execute_tool_call(idx, tool_call):
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the function
                if function_name in self.functions:
                    func = self.functions[function_name]
                    # Check if function is async
                    if asyncio.iscoroutinefunction(func):
                        function_response = await func(**function_args)
                    else:
                        # Run sync function in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        function_response = await loop.run_in_executor(
                            None, lambda f=func, args=function_args: f(**args)
                        )
                else:
                    function_response = {"error": f"Function {function_name} not found"}

                return idx, tool_call.id, function_response

            # Execute all tool calls in parallel
            async def execute_all_tools():
                tasks = [
                    execute_tool_call(idx, tool_call)
                    for idx, tool_call in enumerate(response_message.tool_calls, 1)
                ]
                return await asyncio.gather(*tasks)

            results = await execute_all_tools()

            # Print responses and add to messages
            for idx, tool_call_id, function_response in results:
                print(f"Response {idx}: {json.dumps(function_response, indent=2)}\n")
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(function_response),
                    }
                )

    async def invoke_stream(self, user_query: str):
        start_time = time.time()

        if not self.messages:
            self.messages.append(
                {"role": "system", "content": self.system_prompt},
            )

        self.messages.append(
            {"role": "user", "content": user_query},
        )

        while True:
            response = completion(
                model="anthropic/claude-sonnet-4-20250514",
                messages=self.messages,
                tools=self.schemas,
                stream=True,
            )

            # Collect streamed response
            tool_calls = []

            for chunk in response:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    # Yield content if present
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content

                    # Collect tool calls if present
                    if hasattr(delta, "tool_calls") and delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if tool_call.index is not None:
                                # Extend the tool_calls list if necessary
                                while len(tool_calls) <= tool_call.index:
                                    tool_calls.append(
                                        {
                                            "id": "",
                                            "type": "function",
                                            "function": {"name": "", "arguments": ""},
                                        }
                                    )

                                # Accumulate tool call data
                                if tool_call.id:
                                    tool_calls[tool_call.index]["id"] = tool_call.id
                                if hasattr(tool_call, "function"):
                                    if tool_call.function.name:
                                        tool_calls[tool_call.index]["function"][
                                            "name"
                                        ] = tool_call.function.name
                                    if tool_call.function.arguments:
                                        tool_calls[tool_call.index]["function"][
                                            "arguments"
                                        ] += tool_call.function.arguments

            # If no tool calls were made, we're done
            if not tool_calls or not any(tc.get("id") for tc in tool_calls):
                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"\n{'=' * 60}")
                print(f"Total Time: {elapsed_time:.2f}s")
                print(f"{'=' * 60}\n")
                break

            # Add assistant message with tool calls to conversation
            assistant_message = {"role": "assistant", "content": None, "tool_calls": []}
            for tc in tool_calls:
                if tc.get("id"):
                    assistant_message["tool_calls"].append(
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["function"]["name"],
                                "arguments": tc["function"]["arguments"],
                            },
                        }
                    )

            self.messages.append(assistant_message)

            # Print all tool calls first
            for idx, tool_call in enumerate(assistant_message["tool_calls"], 1):
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                args_str = ", ".join([f'{k}="{v}"' for k, v in function_args.items()])
                print(f"\n\nTool {idx}: {function_name}({args_str})")

            # Execute all tool calls in parallel
            async def execute_tool_call(idx, tool_call):
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute the function
                if function_name in self.functions:
                    func = self.functions[function_name]
                    # Check if function is async
                    if asyncio.iscoroutinefunction(func):
                        function_response = await func(**function_args)
                    else:
                        # Run sync function in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        function_response = await loop.run_in_executor(
                            None, lambda f=func, args=function_args: f(**args)
                        )
                else:
                    function_response = {"error": f"Function {function_name} not found"}

                return idx, tool_call["id"], function_response

            # Execute all tool calls in parallel
            async def execute_all_tools():
                tasks = [
                    execute_tool_call(idx, tool_call)
                    for idx, tool_call in enumerate(assistant_message["tool_calls"], 1)
                ]
                return await asyncio.gather(*tasks)

            results = await execute_all_tools()

            # Print responses and add to messages
            for idx, tool_call_id, function_response in results:
                print(f"Response {idx}: {json.dumps(function_response, indent=2)}\n")
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(function_response),
                    }
                )
