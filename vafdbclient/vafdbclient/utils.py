import sys
import json


def construct_fields_dict(arg_fields):
    """
    Takes a list of field-value pairs: `[[field1, value], [field2, value], ...]`

    Returns a fields dict: `{field1 : [value, value, ...], field2 : [value, value, ...]}`
    """
    fields = {}
    if arg_fields is not None:
        for f, v in arg_fields:
            fields.setdefault(f, []).append(v)
    return fields


def construct_unique_fields_dict(arg_fields):
    """
    Takes a list of field-value pairs: `[[field1, value], [field2, value], ...]`

    Returns a fields dict: `{field1 : value, field2 : value}`

    Raises a `KeyError` for any duplicate fields.
    """
    fields = {}
    if arg_fields is not None:
        for f, v in arg_fields:
            if f in fields:
                raise KeyError(f"Field '{f}' was provided more than once")
            else:
                fields[f] = v
    return fields


def print_response(response, pretty_print=True):
    """
    Print the response and make it look lovely.

    Responses with `response.ok == False` are written to `sys.stderr`.
    """
    if pretty_print:
        indent = 4
    else:
        indent = None

    status_code = f"<[{response.status_code}] {response.reason}>"
    try:
        formatted_response = (
            f"{status_code}\n{json.dumps(response.json(), indent=indent)}"
        )
    except json.decoder.JSONDecodeError:
        formatted_response = f"{status_code}\n{response.text}"

    if response.ok:
        print(formatted_response)
    else:
        print(formatted_response, file=sys.stderr)


def execute_uploads(uploads):
    attempted = 0
    successes = 0
    failures = 0

    try:
        for upload in uploads:
            print_response(upload)

            attempted += 1
            if upload.ok:
                successes += 1
            else:
                failures += 1

    except KeyboardInterrupt:
        print("")

    finally:
        print("[UPLOADS]")
        print(f"Attempted: {attempted}")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
