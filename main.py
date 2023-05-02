import os
from flask import Flask, request, jsonify
import json
import ruamel.yaml
import yaml


app = Flask(__name__)

PROFILES_YAML_FOLDER = "."
NECESSARY_ARGUMENTS = ['--target', '--select']

DBT_PARAMETERS = {
    "run": ["--select", "--exclude", "--selector", "--defer", "--target", "--vars"],
    "test":	["--select", "--exclude", "--selector", "--defer", "--target"],
    "seed":	["--select", "--exclude", "--selector"],
    "snapshot":	["--select", "--exclude" "--selector"],
    "ls": ["--select", "--exclude", "--selector", "--resource-type"],
    "compile":	["--select", "--exclude", "--selector"],
    "freshness":	["--select", "--exclude", "--selector"],
    "build":	["--select", "--exclude", "--selector", "--resource-type", "--defer"]
}
LOG_FIELDS = [
    "unique_id",
    "status",
    "execution_time",
    "message"
]

@app.route('/', methods=['POST'])
def index():
    try:
        envelope = request.get_json()
        print(f" Envelope: {envelope}")
        dbt_command_dict = envelope.get("dbt_command", {})
        if len(dbt_command_dict) == 0:
            return "no dbt commands found, provide them!", 500
        elif len(dbt_command_dict) > 1:
            return "only one command allowed!", 500

        # checks if all commands used are in DBT_PARAMETERS
        # additionally it checks if the NECESSARY_ARGUMENTS are in the call
        # at last it checks if the '--select' value starts with 'tag:'
        for dbt_command, arguments in dbt_command_dict.items():
            if dbt_command not in DBT_PARAMETERS.keys() and not dbt_command.startswith('run-operation '):
                return "An unrecognized dbt command was sent in the request", 500
            for argument in arguments.keys():
                if argument not in DBT_PARAMETERS[dbt_command]:
                    return "Your command argument pairing is not supported by this dbt's version", 500

            if all(key in arguments for key in NECESSARY_ARGUMENTS):
                print(f"{NECESSARY_ARGUMENTS} in call, all good")
            else:
                return f"The dbt command needs a target AND a select param. your command: {arguments}", 500


        execution_string_dbt = _create_exec_string(dbt_command_dict=dbt_command_dict)
        exit_code = os.system(f"{execution_string_dbt}")

        # an exit code of non-zero means dbt failed
        if exit_code != 0:
            return_dict = {
                'message': f"dbt failed and exited with code {exit_code}. Please check the cloud run logs.",
                'invocation_id': _get_logs(raw=True).get('metadata', {}).get('invocation_id')
            }
            return jsonify(return_dict), 500

        ## get logs
        refined_logs = _get_logs()
        return json.dumps(refined_logs), 200

    except:
        return "unhandled server error. Please check the logs.", 500


def _create_exec_string(dbt_command_dict: dict) -> str:
    """function generates the string that should be executed with parameters
        from the request parameters.
    Args:
        dbt_command_dict (dict): dict with the dbt command and command arguments. Needs to follow
            the structure: {"dbt_command":{<command>:{<argument>:<value>}}}
    Returns:
        str: the string that needs to be executed
    """
    if os.environ.get('ENV') == "Local":
        exec_string = "dbt "
    else:
        exec_string = "dbt --log-format json "
    for dbt_command, arguments in dbt_command_dict.items():
        exec_string += dbt_command + " "
        for argument_name, argument_value in arguments.items():
            if type(argument_value) is dict:
                exec_string += f"{argument_name} \'{json.dumps(argument_value)}\' "
            else:
                exec_string += f"{argument_name} {argument_value} "
    # next line expects the profiles.yaml file to be present on project level folder
    exec_string += f"--profiles-dir {PROFILES_YAML_FOLDER}"

    return exec_string


def _get_logs(raw=False) -> list:
    """prepares the return of the api call. Prepares the detailed logs with the models
    Returns:
        list: logs as an list of 1 string (exit code) or many dicts (refined logs)
    """
    if os.path.isfile("target/run_results.json"):
        logs = as_dict("target/run_results.json")
    else:
        logs = "error with run_results.json loading"
    if not raw:
        refined_logs = _refine_logs(logs)
        return refined_logs
    else:
        return logs


def _refine_logs(logs: dict) -> list:
    """refines the detailed logs from dbt to a set of useful information of model
    completion
    Args:
        logs (dict): logs from dbt's run_results.json
    Returns:
        list: list of dicts with refined results
    """
    refined_logs = []

    for i, log in enumerate(logs['results']):
        ## write in a message dict so that it will show directly in the logs
        refined_logs.append({})
        for log_field in LOG_FIELDS:
            if log_field == "message":
                ## customize the log message a bit to be more descriptive
                refined_logs[i].update(
                    {"message": f"{log.get('status')} -- {log.get('message')} for {log.get('unique_id')}"})
            else:
                refined_logs[i].update({log_field: log.get(log_field, "no data for field")})
        refined_logs[i]['generated_at'] = logs['metadata']['generated_at']

    return refined_logs


def as_dict(file_path, keep_comments=False):
    """Returns the data from a file as a dict. Can currently accept paths to json- and yaml-files as an input.
    Args:
        file_path (str): The path to the location of the file.
        keep_comments (bool, optional): Whether to keep the comments in the file, in case of a yaml file. Defaults to
            False.
    Returns:
        dict: The data in the file loaded as a dictionary.
    """
    rua_yaml = ruamel.yaml.YAML()
    extension = file_path.split('.')[-1]
    if extension == 'yml' or extension == 'yaml':
        if keep_comments:
            return rua_yaml.load((open(file_path, 'r')))
        else:
            return yaml.safe_load((open(file_path, 'r')))
    if extension == 'json':
        content_str = open(file_path, 'r').read()
        return json.loads(content_str)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    app.run(host='0.0.0.0', port=PORT, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
