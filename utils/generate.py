import yaml
import json
from inflection import camelize
from jinja2 import Environment, FileSystemLoader


def process_packets(data):
    packets = []
    for packet_description in data["packets"]:
        new_packet = {
            "class": camelize(packet_description["name"]),
            "id": "0" + repr(packet_description["id"]).replace('\'', '').lstrip('\\'),
            "fields": [],
            "structure": []
        }
        for field in packet_description["structure"]:
            if field["type"] == "__magic__":
                new_packet["structure"].append(field["type"])
                continue
            new_packet["structure"].append(field["name"])
            new_packet["fields"].append({
                "name": field["name"],
                "class": camelize("{}_field".format(field["type"])),
                "options": field.get("options", dict())
            })
        packets.append(new_packet)
    return packets


with open("resources/packets.yml") as yaml_file:
    packets = yaml.load(yaml_file)

environment = Environment(loader=FileSystemLoader("resources"), trim_blocks=True)
template = environment.get_template("packets.py.jinja")

with open("rakpy/protocol/packets.py", "w") as destination_file:
    destination_file.write(template.render(packets=process_packets(packets)))

# generate json for convenience
with open("resources/packets.json", "w") as destination_file:
    json.dump(packets, destination_file, indent=4)
