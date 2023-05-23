#!/usr/bin/env python3

import json
import base64
import requests
import argparse


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", type=str, default="")
    # add parser for ip, port, image_name and json_link
    parser.add_argument("-e", "--endpoint", type=str, default="127.0.0.1:7861")
    parser.add_argument("-o", "--out", type=str, default="")
    parser.add_argument(
        "-f", "--file", type=str, default="", help="json file path"
    )
    parser.add_argument(
        "-j", "--json", type=str, default="", help="json file path"
    )

    args = parser.parse_args()
    return args


def submit_post(url: str, data: dict):
    """
    Submit a POST request to the given URL with the given data.
    """
    return requests.post(url, data=json.dumps(data))


def save_encoded_image(b64_image: str, output_path: str):
    """
    Save the given image to the given output path.
    """
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(b64_image))


def get_current_checkpoint_name(endpoint):
    options_url = f"http://{endpoint}/sdapi/v1/options/"
    return requests.get(options_url).json()["sd_model_checkpoint"]


def get_all_models_name(endpoint):
    sd_models_url = f"http://{endpoint}/sdapi/v1/sd-models/"
    models_info = requests.get(sd_models_url).json()
    titles = [item["title"] for item in models_info]
    model_names = [item["model_name"] for item in models_info]
    return dict(zip(model_names, titles))


def find_formal_name(quest_ckpt_name, endpoint):
    all_models = get_all_models_name(endpoint)
    for model_name, title in all_models.items():
        # check if quest_ckpt_name is a prefix of model_name
        if model_name.startswith(quest_ckpt_name):
            return title


def change_ckpt(formal_name, endpoint):
    options_url = f"http://{endpoint}/sdapi/v1/options/"
    submit_post(options_url, {"sd_model_checkpoint": formal_name})


def text2image():
    args = parse()
    endpoint = args.endpoint
    image_name = args.out
    json_link = args.json if args.json else args.file

    if not image_name.endswith(".png"):
        image_name = image_name + ".png"

    with open(json_link) as json_file:
        payload = json.load(json_file)
    current_ckpt_name = get_current_checkpoint_name(endpoint)
    quest_ckpt_name = payload["sd_model_checkpoint"]
    formal_name = find_formal_name(quest_ckpt_name, endpoint)

    if current_ckpt_name != quest_ckpt_name:
        change_ckpt(formal_name, endpoint)

    txt2img_url = f"http://{endpoint}/sdapi/v1/txt2img"
    response = submit_post(txt2img_url, payload)
    save_encoded_image(response.json()["images"][0], f"{image_name}")
    return image_name


if __name__ == "__main__":
    print(text2image())
