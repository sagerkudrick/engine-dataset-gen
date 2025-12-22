FROM linuxserver/blender:5.0.1

WORKDIR /workspace

COPY engine-dataset-gen.blend dataset-gen.py /workspace/

VOLUME ["/workspace/output"]

CMD ["blender", "engine-dataset-gen.blend", "--background", "--python", "dataset-gen.py", "--", "--num_samples", "23000"]
