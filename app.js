const express = require("express");
const fileUpload = require("express-fileupload");
const fs = require("fs");
const uuid = require("uuid/v4");
const cp = require("child_process");
var superchild = require("superchild");
const { stdout } = require("process");

const app = express();
app.use(fileUpload());

const port = 5001;

var commands = {
  js: {
    run: "node",
  },
};

app.post("/compile", (req, res) => {
  if (Object.keys(req.files).length !== 2) {
    return res.status(400).send({ client: "Files not uploaded." });
  }

  var retObject = {};
  const reqId = uuid().toString("utf-8");
  inputs = req.files.inputs;
  functions = req.files.functions;

  inputsData = JSON.parse(inputs.data.toString("utf-8"));

  switch (functions.name.split(".").pop()) {
    // Javascript case
    case "js":
      outputPath = "./fileManager/" + reqId + "output.js";

      inputsData.inputs.forEach((input) => {
        functions.mv(outputPath, () => {
          fs.appendFileSync(
            outputPath,
            `\nconsole.log(${inputsData.name + `(${input})`})`
          );
          var child = cp.spawn("ls");
          child.stdout.on("data", (data) => console.log(data.toString()));
          child.stderr.on("data", (data) => console.log(data));
          child.on("error", (data) => console.log(data));
          fs.unlinkSync(outputPath);
        });
      });
      break;

    default:
      return res.status(400).send({ client: "File type not supported." });
  }
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
