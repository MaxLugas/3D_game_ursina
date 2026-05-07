from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

import sys
import os


class FBXToBam(ShowBase):
    def __init__(self):
        loadPrcFileData("", "window-type none")
        super().__init__()

    def convert(self, input_path):
        print(f"📂 loading: {input_path}")

        actor = Actor(input_path)

        if actor.isEmpty():
            print("❌ failed to load FBX")
            return

        # важно: не ломаем скелет
        actor.clearTransform()

        output_path = os.path.splitext(input_path)[0] + ".bam"

        print(f"💾 writing: {output_path}")
        actor.writeBamFile(output_path)

        print("✅ done")


def main():
    if len(sys.argv) < 2:
        print("usage: python fbx2bam.py model.fbx")
        return

    app = FBXToBam()
    app.convert(sys.argv[1])
    app.destroy()


if __name__ == "__main__":
    main()