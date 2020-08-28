from flask import Flask, request
import json
import uuid
import os
import shutil
import subprocess

app = Flask(__name__)

cwd = os.getcwd()

info = {
    "java": {
        "command": "java",
        "uniquecode": "// codenite-java"
    }
}


@ app.route('/compile', methods=['POST'])
def compile():
    if len(request.files) != 2:
        return json.dumps({"client": "Files not uploaded."})

    returnList = []
    reqId = str(uuid.uuid4())

    inputsFile = request.files['inputs']
    functionsFile = request.files['functions']

    inputsData = json.loads(inputsFile.read())

    extension = functionsFile.filename.split(".")[-1]
    returntype = inputsData['returntype']
    inputs = inputsData['loglines'][extension]

    functionPath = cwd + "/fileManager/" + reqId + "function." + extension
    outputPath = cwd + "/fileManager/" + reqId + "output." + extension

    command = [info[extension]['command'], outputPath]
    uniquecode = info[extension]['uniquecode']

    functionsFile.save(functionPath)

    for input in inputs:
        shutil.copyfile(functionPath, outputPath)
        with open(outputPath, 'r') as file:
            filedata = file.read()
            filedata = filedata.replace(uniquecode, input)
        with open(outputPath, 'w') as file:
            file.write(filedata)
        program = subprocess.run(command, shell=False,
                                 capture_output=True, universal_newlines=True)
        stdout = program.stdout.split('\n')
        stderr = program.stderr
        if(program.returncode == 0):
            try:
                output = parser(returntype, stdout[-4])
                expected = parser(returntype, stdout[-3])
                result = boolparser(stdout[-2])
                returnObj = {"output": output,
                             "expected": expected, "result": result}
            except:
                stderr = "solution do not matches the return type."
                returnObj = {"stderr": stderr}
        else:
            returnObj = {"stderr": stderr}
        returnList.append(returnObj)

    # os.remove(functionPath)
    # os.remove(outputPath)

    return json.dumps(returnList)


def parser(returntype, variable):
    if(returntype == "int"):
        variable = int(variable)
    elif(returntype == "float"):
        variable = float(variable)
    elif(returntype == "arr"):
        variable = json.loads(variable)
    elif(returntype == "bool"):
        variable = boolparser(variable)
    else:
        variable = variable

    return variable


def boolparser(variable):
    if(variable == "false" or variable == "False"):
        variable = False
    elif(variable == "true" or variable == "True"):
        variable = True
    else:
        raise Exception("Something is wrong, I can feel it.")

    return variable


if __name__ == '__main__':
    app.run(port=5001, debug=True)
