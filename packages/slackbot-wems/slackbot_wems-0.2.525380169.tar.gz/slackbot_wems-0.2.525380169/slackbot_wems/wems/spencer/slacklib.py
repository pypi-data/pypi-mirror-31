# Put your commands here
COMMAND1 = "spencer test"
COMMAND2 = "joi test"
COMMAND3 = "12*100*160"

# Your handling code goes in this function
def handle_command(command):
    """
        Determine if the command is valid. If so, take action and return
        a response, if necessary.
    """
    response = ""
    if COMMAND1 in command:
        response = "spencer's test passed"
    if COMMAND2 in command:
        response = "joe test passed"
    if COMMAND3 in command:
        response = "192000"
        
    return response

