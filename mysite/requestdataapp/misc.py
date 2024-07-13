file_extensions = {
    "image_type": ['.jpg', '.jpeg', '.png', '.gif'],
    "video_type": ['.mp4', '.avi', '.mov'],
    "docs_type": ['.txt', '.doc', '.pdf'],
    "audio_type": ['.mp3', '.wav', '.aac', '.flac', '.ogg']
}


def check_file_type(file_name: str) -> str:
    if any(file_name.endswith(file_type) for file_type in file_extensions["image_type"]):
        return "data/images"

    elif any(file_name.endswith(file_type) for file_type in file_extensions["video_type"]):
        return "data/video"

    elif any(file_name.endswith(file_type) for file_type in file_extensions["docs_type"]):
        return "data/docs"

    elif any(file_name.endswith(file_type) for file_type in file_extensions["audio_type"]):
        return "data/audio"

    else:
        return "data/misc"


def convert_file_size(file_size: int, notation: str):
    if notation == 'kbytes':
        return round(file_size / 1024, 2)

    elif notation == 'mbytes':
        return round(file_size / 1048576, 2)

    elif notation == 'gbytes':
        return round(file_size / 1073741824, 2)

    else:
        return file_size
