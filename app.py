from flask import Flask, request, jsonify, Response
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
        return jsonify({"error": "files not uploaded"})

    returnList = []
    reqId = str(uuid.uuid4())

    inputsFile = request.files['inputs']
    functionsFile = request.files['functions']

    inputsData = json.loads(inputsFile.read())

    extension = functionsFile.filename.split(".")[-1]
    returntype = inputsData['returntype']
    inputs = inputsData['inputs'][extension]

    functionPath = cwd + "/fileManager/" + reqId + "function." + extension
    outputPath = cwd + "/fileManager/" + reqId + "output." + extension

    uniquecode = ""

    if(extension == "py"):
        uniquecode = "# codenite-"+extension
    else:
        uniquecode = "// codenite-"+extension

    functionsFile.save(functionPath)

    for input in inputs:
        shutil.copyfile(functionPath, outputPath)
        with open(outputPath, 'r') as file:
            filedata = file.read()
            if(filedata.count(uniquecode) == 1):
                filedata = filedata.replace(uniquecode, input)
            else:
                os.remove(functionPath)
                os.remove(outputPath)
                return jsonify({"stderr": "donot mess with code outside the function please."})
        with open(outputPath, 'w') as file:
            file.write(filedata)
        program = getcommand(extension, outputPath, reqId)
        stdout = program.stdout.split('\n')
        stderr = program.stderr
        if(program.returncode != 0):
            os.remove(functionPath)
            os.remove(outputPath)
            return jsonify({"stderr": stderr})
        try:
            output = parser(returntype, stdout[-2])
        except:
            os.remove(functionPath)
            os.remove(outputPath)
            return jsonify({"stderr": "solution donot match the retutn type."})
        returnList.append(output)

    os.remove(functionPath)
    os.remove(outputPath)
    print(returnList)
    return jsonify({"stdout": returnList})


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


def getcommand(extension, path, reqId):
    if(extension == 'py'):
        command = ("python " + path).split(" ")
        return subprocess.run(command, capture_output=True, universal_newlines=True, shell=False)
    elif(extension == "js"):
        command = ("node " + path).split(" ")
        return subprocess.run(command, capture_output=True, universal_newlines=True, shell=False)
    elif(extension == "java"):
        command = ("java " + path).split(" ")
        return subprocess.run(command, capture_output=True, universal_newlines=True, shell=False)
    elif(extension == "cpp"):
        outpath = cwd + "/fileManager/" + reqId
        command = "g++ " + path + " -o " + outpath
        program = subprocess.run(command.split(
            " "), capture_output=True, universal_newlines=True, shell=False)
        if(program.returncode == 0):
            program = subprocess.run((outpath).split(
                " "), capture_output=True, universal_newlines=True, shell=False)
        return program
    elif(extension == "ts"):
        command = ("ts-node " + path).split(" ")
        return subprocess.run(command, capture_output=True, universal_newlines=True, shell=False)
    elif(extension == "cs"):
        outpath = cwd + "/fileManager/" + reqId
        command = "mcs -out:" + outpath + " " + path
        program = subprocess.run(command.split(
            " "), capture_output=True, universal_newlines=True, shell=False)
        if(program.returncode == 0):
            program = subprocess.run((outpath).split(
                " "), capture_output=True, universal_newlines=True, shell=False)
        return program


if __name__ == '__main__':
    app.run(port=5001, debug=True)
