import socket
import api
import argparse
import api

# region Predefined

# The following are for convenience. You can use them to build expressions.
pi_c = api.NAMED_CONSTANTS.PI
tau_c = api.NAMED_CONSTANTS.TAU
e_c = api.NAMED_CONSTANTS.E

add_b = api.BINARY_OPERATORS.ADD
sub_b = api.BINARY_OPERATORS.SUB
mul_b = api.BINARY_OPERATORS.MUL
div_b = api.BINARY_OPERATORS.DIV
mod_b = api.BINARY_OPERATORS.MOD
pow_b = api.BINARY_OPERATORS.POW

neg_u = api.UNARY_OPERATORS.NEG
pos_u = api.UNARY_OPERATORS.POS

sin_f = api.FUNCTIONS.SIN
cos_f = api.FUNCTIONS.COS
tan_f = api.FUNCTIONS.TAN
sqrt_f = api.FUNCTIONS.SQRT
log_f = api.FUNCTIONS.LOG
max_f = api.FUNCTIONS.MAX
min_f = api.FUNCTIONS.MIN
pow_f = api.FUNCTIONS.POW
rand_f = api.FUNCTIONS.RAND


# endregion


def process_response(response: api.CalculatorHeader) -> None:
    if response.is_request:
        raise api.CalculatorClientError("Got a request instead of a response")
    if response.status_code == api.CalculatorHeader.STATUS_OK:
        result, steps = api.data_to_result(response)
        print("Result:", result)
        if steps:
            print("Steps:")
            expr, first, *rest = steps
            print(f"{expr} = {first}", end="\n" * (not bool(rest)))
            if rest:
                print(
                    "".join(map(lambda v: f"\n{' ' * len(expr)} = {v}", rest)))
    elif response.status_code == api.CalculatorHeader.STATUS_CLIENT_ERROR:
        err = api.data_to_error(response)
        raise api.CalculatorClientError(err)
    elif response.status_code == api.CalculatorHeader.STATUS_SERVER_ERROR:
        err = api.data_to_error(response)
        raise api.CalculatorServerError(err)
    else:
        raise api.CalculatorClientError(
            f"Unknown status code: {response.status_code}")


def client(arr, server_address: tuple[str, int], expression: api.Expression, show_steps: bool = False,
           cache_result: bool = False, cache_control: int = api.CalculatorHeader.MAX_CACHE_CONTROL) -> None:
    server_prefix = f"{{{server_address[0]}:{server_address[1]}}}"

    # Using with statement to manage the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        print(f"{server_prefix} Connection established")

        while True:
            try:
                #for infinity time on proxy cache control need to be CalculatorHeader.MAX_CACHE_CONTROL
                request = api.CalculatorHeader.from_expression(
                    expression, show_steps, cache_result, cache_control)
                request = request.pack()
                print(f"{server_prefix} Sending request of length {len(request)} bytes")
                client_socket.sendall(request)

                response = client_socket.recv(api.BUFFER_SIZE)
                print(f"{server_prefix} Got response of length {len(response)} bytes")
                response = api.CalculatorHeader.unpack(response)
                process_response(response)

            except api.CalculatorError as e:
                print(f"{server_prefix} Got error: {str(e)}")
            except Exception as e:
                print(f"{server_prefix} Unexpected error: {str(e)}")
            inputt = input("Please chose an expression to calculate from 1-6, to exit press 7: ")
            # handeling all sort of incorrect inputes from the client.
            while not inputt.isdigit() or (int(inputt) > 7 or int(inputt) < 1):
                print("invalid input try again")
                inputt = input("Please chose an expression to calculate from 1-6, to exit press 7: ")
            # casting inputt back to int after handung all casses so that we don't have to cast it again everytime
            inputt = int(inputt)
            if inputt == 7:
                print("client closed")
                break
            # here the client chosses if he wants to see the steps or not + we handeled edge cases
            showsteps = input("Y-showsteps, N-only final answer\n" + "please chose:")
            if showsteps.upper() == "N":
                show_steps = False
            elif showsteps.upper() == "Y":
                show_steps = True
            while showsteps.upper() != "Y" and showsteps.upper() != "N":
                print("please be careful to write in uppercase")
            #here we send the new expression.
            expression = arr[inputt - 1]


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="A Calculator Client.")

    arg_parser.add_argument("-p", "--port", type=int,
                            default=api.DEFAULT_PROXY_PORT, help="The port to connect to.")
    arg_parser.add_argument("-H", "--host", type=str,
                            default=api.DEFAULT_PROXY_HOST, help="The host to connect to.")

    args = arg_parser.parse_args()
    host = args.host
    port = args.port

    # here we defined the 6 expressions the client can choose from:
    expr = mul_b(div_b(sin_f(max_f(2, mul_b(3, 4), 5, mul_b(
        6, div_b(mul_b(7, 8), 9)), div_b(10, 11))), 12), 13)  # (1)
    expr2 = add_b(max_f(2, 3), 3)  # (2)
    expr3 = add_b(3, div_b(mul_b(4, 2), pow_b(sub_b(1, 5), pow_b(2, 3))))  # (3)
    expr4 = div_b(pow_b(add_b(1, 2), mul_b(3, 4)), mul_b(5, 6))  # (4)
    expr5 = neg_u(neg_u(pow_b(add_b(1, add_b(2, 3)), neg_u(add_b(4, 5)))))  # (5)
    expr6 = max_f(2, mul_b(3, 4), log_f(e_c), mul_b(6, 7), div_b(9, 8))  # (6)
    expr7="stop"

    # we put the expressions in an array in order to send all the expressions to the client function.
    arr = [expr, expr2, expr3, expr4, expr5, expr6]

    show_steps = False  # Request the steps of the calculation this is the default because the client can choose.
    cache_result = True  # Request to cache the result of the calculation

    # If the result is cached, this is the maximum age of the cached response
    # that the client is willing to accept (in seconds)
    cache_control = 2 ** 16 - 1

    print("here are the expresssions you need to choose from\n")
    print("1." + str(expr) + "\n" + "2." + str(expr2) + "\n" + "3." + str(expr3) + "\n" +
          "4." + str(expr4) + "\n" + "5" + str(expr5) + "\n" + "6." + str(expr6) + "\n" + "7." + str(expr7) + "\n")

    # here we handle the clients input only for the first time:
    inputt = input("Please chose an expression to calculate from 1-6: ")

    # handeling all sort of incorrect inputes from the client.
    while not inputt.isdigit() or (int(inputt) > 6 or int(inputt) < 1):

        print("invalid input try again")
        inputt = input("Please chose an expression to calculate from 1-6: ")
    # casting inputt back to int after handung all casses so that we don't have to cast it again everytime

    inputt = int(inputt)
    # here the client chosses if he wants to see the steps or not + we handeled edge cases

    showsteps = input("Y-showsteps, N-only final answer\n" + "please chose:")
    if showsteps.upper() == "N":
        show_steps = False
    elif showsteps.upper() == "Y":
        show_steps = True
    while showsteps.upper() != "Y" and showsteps.upper() != "N":
        print("please be careful to choose a correct answer")
        showsteps = input("Y-showsteps, N-only final answer\n" + "please chose:")


    # sends to client the array of expressions and all the relevant fields needed in order to send the clients first request.
    client(arr, (host, port), arr[inputt - 1], show_steps, cache_result=True, cache_control=120)
