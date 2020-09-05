import os
from Constants import DATA_PATH

# script removing duplicate files from directories under DATA_PATH

if __name__ == "__main__":

    for directory in os.listdir(DATA_PATH):

        deleted_count = 0
        last_content = b''

        for filename in sorted(os.listdir(f"{DATA_PATH}/{directory}")):

            file_path = f"{DATA_PATH}/{directory}/{filename}"

            with open(file_path, "rb") as f:
                content = f.read()

            if last_content == content:
                deleted_count += 1
                os.remove(file_path)

            last_content = content

        print(f"deleted {deleted_count} files in {directory}")
