from pathlib import Path

import proto.line_pb2 as line_pb2
import random
import base64
import json
import gzip

from google.protobuf.json_format import MessageToJson



# 0.7878971099853516 mb
# os.stat_result(st_mode=33188, st_ino=21242058, st_dev=16777233, st_nlink=1, st_uid=501, st_gid=20, st_size=1101582, st_atime=1673941041, st_mtime=1673941113, st_ctime=1673941113)
# File Size in Bytes is 1101582
# File Size in MegaBytes is 1.0505504608154297
# os.stat_result(st_mode=33188, st_ino=21242058, st_dev=16777233, st_nlink=1, st_uid=501, st_gid=20, st_size=880874, st_atime=1673941041, st_mtime=1673941113, st_ctime=1673941113)
# File Size in Bytes is 880874
# File Size in MegaBytes is 0.8400669097900391
def main():
    points_count = 30
    strokes_count = 50
    msg = line_pb2.DataEntry()
    msg.labelType = line_pb2.LabelType.Value("LATEX")
    msg.label = '\gamma^2+\theta^2=\omega^2 \gamma^2+\theta^2=\omega^2'
    msg.source = "cdatai5"
    msg.userID = "2beec221-2277-4139-93c5-f854f476e05b"
    msg.deviceID = "537745b7-adda-4837-b054-2e4eb060d46c"
    msg.id = "9e653fe8-82bb-46e0-8a8a-32838db1c0e5"

    for _ in range(strokes_count):
        stroke = msg.strokes.add()
        stroke.firstPointTimeStamp = random.randint(1, 1000000000)
        stroke.firstPointX = random.random()
        stroke.firstPointY = random.random()
        for _ in range(points_count):
            point = stroke.points.add()
            point.deltaX = random.random()
            point.deltaY = random.random()
            point.deltaT = random.randint(1, 1000000000)

    # base64.encode()
    print(str(msg.ByteSize() / 1024 / 1024) + " mb")
    data_str = base64.b64encode(msg.SerializeToString()).decode("utf-8")

    parsed_msg = line_pb2.DataEntry()
    parsed_msg.ParseFromString(base64.b64decode(data_str.encode('utf-8')))

    assert parsed_msg == msg
    json_path = Path(__file__).parent / "output.json"
    with (json_path).open(mode="w") as f:
        json.dump({"data": data_str, "v": "1"}, f)

    print_file_size(str(json_path))

    json_str = MessageToJson(msg)
    json_obj = json.loads(json_str)
    json_path = Path(__file__).parent / "output_json.json"
    with (json_path).open(mode="w") as f:
        json.dump(json_obj, f, indent=2)

    print_file_size(str(json_path))
    # data_str_gzip = base64.b64encode(gzip.compress(msg.SerializeToString())).decode("utf-8")
    # parsed_msg = line_pb2.DataEntry()
    # parsed_msg.ParseFromString(
    #     gzip.decompress(
    #         base64.b64decode(
    #             data_str_gzip.encode('utf-8')
    #         )
    #     )
    # )
    # assert parsed_msg == msg
    #
    # json_path = Path(__file__).parent / "output.json"
    # with (json_path).open(mode="w") as f:
    #     json.dump({"data": data_str_gzip, "v": "1"}, f)
    #
    # print_file_size(str(json_path))


def print_file_size(file_name: str):
    import os
    file_stats = os.stat(file_name)
    print(file_stats)
    print(f'File Size in Bytes is {file_stats.st_size}')
    print(f'File Size in MegaBytes is {file_stats.st_size / (1024 * 1024)}')


if __name__ == '__main__':
    main()
