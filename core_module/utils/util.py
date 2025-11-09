import inspect
import urllib


def get_caller_function_info(frame_depth=1):
    """
    Retrieves the name and parameters of a function in the call stack.

    :param frame_depth: The number of frames to move up the stack (default is 1, i.e., direct caller).
    :return: A dictionary with the function's name and its parameters.
    """
    # Get the current stack frame
    current_frame = inspect.currentframe()

    # Traverse the stack based on the frame_depth
    target_frame = current_frame
    for _ in range(frame_depth):
        if target_frame is None:
            raise ValueError("Frame depth exceeds the available call stack.")
        target_frame = target_frame.f_back  # Go one level up in the stack

    if target_frame is None:
        return {
            "function_name": None,
            "parameters": {},
        }

    # Get the target function's name
    target_function_name = target_frame.f_code.co_name

    # Get arguments from the target frame
    arg_info = inspect.getargvalues(target_frame)
    args, kwargs = arg_info.args, arg_info.locals

    # Build a dictionary of parameters and their values
    target_parameters = {
        arg: kwargs.get(arg, None) for arg in args
    }

    return {
        "function_name": target_function_name,
        "parameters": target_parameters
    }


def generate_file_name_from_function_info(data=None, frame_depth=3):
    """
    Creates a file name from an object containing function_name and parameters.

    :param frame_depth: depends on where you call it from
    :param data: Dictionary containing "function_name" and "parameters".
                 Example: {"function_name": "parent_function_example", "parameters": {"param1": 1, "param2": 2}}
    :return: A string representing the file name.
    """
    if data is None:
        data = get_caller_function_info(frame_depth=frame_depth)

    function_name = data.get("function_name", "unknown_function")
    parameters = data.get("parameters", {})

    # Serialize parameters into a URL-safe string
    parameter_string = "_".join(
        f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in parameters.items()
    )

    # Construct the file name (add parameters if present)
    file_name = f"{function_name}_{parameter_string}.json"

    # Make the file name safe by removing invalid characters for a file system
    file_name = file_name.replace(" ", "_").replace("/", "_")

    # Remove trailing underscore if parameter_string is empty
    if file_name.endswith("_.json"):
        file_name = file_name.replace("_.json", ".json")


    return file_name



def debug_print(*args, **kwargs):
    """
    Custom print function that includes the call stack chain (file names and line numbers)
    in reverse order and prints a structured debug message.

    Args:
        *args: Positional arguments to print as the message.
        **kwargs: Keyword arguments to pass to the built-in print.
    """
    # Retrieve the call stack
    stack = inspect.stack()

    # Build the call chain excluding the current debug_print call (stack[0])
    call_chain = []
    for frame in stack[1:]:  # Start from the caller of debug_print (stack[1])
        filename = frame.filename.split('/')[-1].split('\\')[-1]  # Get only the file name
        line_number = frame.lineno
        call_chain.append(f"{filename}:{line_number}")

    # Reverse the call chain list
    call_chain.reverse()

    # Join the call chain with the ASCII delineator
    call_chain_str = " --> ".join(call_chain)

    # Format the final debug message
    message = " ".join(map(str, args))  # Combine the message in args
    final_message = f"{call_chain_str} {message}"

    # Print the message
    print(final_message, **kwargs)


if __name__ == "__main__":
    def function_a():
        function_b()


    def function_b():
        function_c()


    def function_c():
        debug_print("Custom message from function_c.")

    function_a()