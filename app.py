from flask import Flask, request
import json
import uuid
import os
import shutil
import subprocess

app = Flask(__name__)

cwd = os.getcwd()


@ app.route('/compile', methods=['POST'])
def compile():
    if len(request.files) != 2:
        return json.dumps({"client": "Files not uploaded."})

    returnList = []

    reqId = str(uuid.uuid4())
    inputs = request.files['inputs']
    functions = request.files['functions']

    inputsData = json.loads(inputs.read())
    extension = functions.filename.split(".")[-1]

    if extension == "js":
        returntype = inputsData['returntype']
        functionPath = cwd + "/fileManager/" + reqId + "function.js"
        outputPath = cwd + "/fileManager/" + reqId + "output.js"
        command = ("node " + outputPath).split(" ")
        functions.save(functionPath)
        for input in inputsData['inputs']:
            shutil.copyfile(functionPath, outputPath)
            with open(outputPath, "a") as output:
                output.write("\nconsole.log(%s(%s))" %
                             (inputsData['name'], input))
            program = subprocess.run(
                command, shell=False, capture_output=True, universal_newlines=True)

            stdout = ""
            stderr = program.stderr

            if program.returncode == 0:
                stdout = program.stdout.split("\n")[-2]
                if returntype == "int":
                    try:
                        stdout = int(stdout)
                    except:
                        stdout = ""
                        stderr = "function expected to return an integer"
                elif returntype == "bool":
                    if stdout == "true":
                        stdout = True
                    elif stdout == "false":
                        stdout = False
                    else:
                        stdout = ""
                        stderr = "function expected to return true or false"
                elif returntype == "float":
                    try:
                        stdout = float(stdout)
                    except:
                        stdout = ""
                        stderr = "function expected to return a decimal number"
                elif returntype == "arr":
                    try:
                        stdout = json.loads(stdout)
                    except:
                        stdout = ""
                        stderr = "function expected to return an array or a list"
            returnList.append(
                {"input": input, "stdout": stdout, "stderr": stderr})

        os.remove(functionPath)
        os.remove(outputPath)

        return json.dumps(returnList)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
