import bayes3d as b
import numpy as np
import bayes3d.transforms_3d as t3d
import jax.numpy as jnp
import meshcat.geometry as g
import trimesh
import os

b.setup_visualizer()

b.clear()

cloud = np.random.rand(1000,3) * 1.0
b.show_cloud("c1", cloud - 1.0)
b.show_cloud("c2", cloud + 4.0, color=np.array([1.0, 0.0, 0.0]))

pose = t3d.transform_from_pos(jnp.array([0.0, 0.0, 1.0]))
mesh = trimesh.load(os.path.join(b.utils.get_assets_dir(), "sample_objs/cube.obj"))
mesh = b.mesh.scale_mesh(mesh, 0.1)
b.show_trimesh("obj", mesh)
b.set_pose("obj", pose)

pose = t3d.transform_from_pos(jnp.array([1.0, 0.0, 2.0]))
b.show_pose("pose", pose)

from IPython import embed; embed()