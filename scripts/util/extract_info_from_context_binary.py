# ---------------------------------------------------------------------
# Copyright (c) 2025 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------

import argparse
import json
import os
import subprocess

QNN_TYPE_TO_STR = {
    "QNN_DATATYPE_UFIXED_POINT_16": "uint16",
    "QNN_DATATYPE_UFIXED_POINT_8": "uint8",
    "QNN_DATATYPE_INT_32": "int32",
}


def validate_qnn_sdk_path(qnn_sdk):
    # Must be an absolute path
    if not os.path.isabs(qnn_sdk):
        raise ValueError("The --qnn path must be an absolute path")
    # Disallow '..' and spaces in path components for extra safety
    if ".." in qnn_sdk or " " in qnn_sdk:
        raise ValueError("The --qnn path cannot contain '..' or spaces")
    # Check that the sdk path exists and is a directory
    if not os.path.isdir(qnn_sdk):
        raise ValueError("The --qnn path does not exist or is not a directory")

def run_utility(qnn_sdk, model_path):
    exec_path = f"{qnn_sdk}/qnn_sdk/default/bin/x86_64-linux-clang/qnn-context-binary-utility"
    if not os.path.isfile(exec_path):
        raise FileNotFoundError(f"Could not find qnn-context-binary-utility at {exec_path}")
    json_path = f"{os.path.splitext(os.path.basename(model_path))[0]}.json"
    subprocess.run(
        [
            exec_path,
            "--context_binary",
            model_path,
            "--json_file",
            json_path,
        ]
    )
    return json_path


def print_details_from_json(json_path):
    data = json.load(open(json_path))

    for graph in data["info"]["graphs"]:
        print(f"Graph Name: {graph['info']['graphName']}")
        input_spec = dict()
        for input in graph["info"]["graphInputs"]:
            input_spec[input["info"]["name"]] = (
                tuple(input["info"]["dimensions"]),
                QNN_TYPE_TO_STR[input["info"]["dataType"]],
            )
        print(f"Graph Input: {input_spec}")
        out = []
        for output in graph["info"]["graphOutputs"]:
            out.append(output["info"]["name"])
        print(f"Graph Output Names: {out}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=None,
        help="Folder of context binaries whose graph names and input/output details are needed to create model.py",
    )
    parser.add_argument(
        "--qnn",
        type=str,
        default=None,
    validate_qnn_sdk_path(args.qnn)
        help="QNN SDK path",
    )
    args = parser.parse_args()
    assert args.qnn and args.model, "Must specify --model and --qnn"

    for model_path in os.listdir(args.model):
        if os.path.splitext(model_path)[-1] == ".bin":
            print("===================")
            json_path = run_utility(args.qnn, os.path.join(args.model, model_path))
            print_details_from_json(json_path)
            print()
            print()


if __name__ == "__main__":
    main()
