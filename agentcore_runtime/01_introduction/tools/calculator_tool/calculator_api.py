import json


def calculate(operation, num1, num2):
    try:
        num1 = float(num1)
        num2 = float(num2)

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return json.dumps(
                    {
                        "error": "Division by zero is not allowed",
                        "operation": operation,
                        "num1": num1,
                        "num2": num2,
                    }
                )
            result = num1 / num2
        else:
            return json.dumps(
                {
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": ["add", "subtract", "multiply", "divide"],
                }
            )

        return json.dumps(
            {"operation": operation, "num1": num1, "num2": num2, "result": result}
        )

    except ValueError as e:
        return json.dumps({"error": f"Invalid number format: {str(e)}"})
