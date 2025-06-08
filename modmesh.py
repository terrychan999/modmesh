import os
os.environ["QT3D_RENDERER"] = "opengl"
from modmesh.pilot import launch
if __name__ == "__main__":
    launch()
