from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys
import os


class Converter(ShowBase):
    def __init__(self):
        loadPrcFileData("", "window-type none")
        super().__init__()

    def convert(self, input_path):
        print(f"loading: {input_path}")

        model = self.loader.loadModel(input_path)
        if model.isEmpty():
            print("failed to load model")
            return

        output_path = os.path.splitext(input_path)[0] + ".bam"

        print(f"writing: {output_path}")
        model.writeBamFile(output_path)

        print("done ✅")


def main():
    if len(sys.argv) < 2:
        print("usage: python glb2bam.py model.glb")
        return

    app = Converter()
    app.convert(sys.argv[1])
    app.destroy()


if __name__ == "__main__":
    main()