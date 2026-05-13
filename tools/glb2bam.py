from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys
import os


class Converter(ShowBase):
    def __init__(self):
        loadPrcFileData("", "window-type none")
        super().__init__()

    def convert(self, input_path):
        abs_input_path = os.path.abspath(input_path)

        if not os.path.exists(abs_input_path):
            print(f"❌ File not found: {abs_input_path}")
            return

        print(f"Loading: {abs_input_path}")

        model = self.loader.loadModel(abs_input_path)
        if model.isEmpty():
            print("❌ Failed to load model")
            return

        model.setP(90)

        filename_no_ext = os.path.splitext(os.path.basename(abs_input_path))[0]

        output_dir = "models_bam"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, filename_no_ext + ".bam")

        model.writeBamFile(output_path)

        print("✅ Done")

def main():
    if len(sys.argv) < 2:
        print("usage: python glb2bam.py models_glb/model.glb")
        return

    app = Converter()
    app.convert(sys.argv[1])
    app.destroy()


if __name__ == "__main__":
    main()