from tensorflow_probability.substrates import jax as tfp
import jax
import jax.numpy as jnp
from .transforms_3d import (
    quaternion_to_rotation_matrix,
    rotation_matrix_to_quaternion
)
from jax.scipy.special import logsumexp


def gaussian_pose(key, covar):
    translation = tfp.distributions.MultivariateNormalFullCovariance(jnp.zeros(3), covar).sample(seed=key)
    return jnp.vstack(
        [jnp.hstack([jnp.eye(3), translation.reshape(3,1) ]), jnp.array([0.0, 0.0, 0.0, 1.0])]
    )

def vmf(key, concentration):
    translation =jnp.zeros(3)
    quat = tfp.distributions.VonMisesFisher(
        jnp.array([1.0, 0.0, 0.0, 0.0]), concentration
    ).sample(seed=key)
    rot_matrix =  quaternion_to_rotation_matrix(quat)
    return jnp.vstack(
        [jnp.hstack([rot_matrix, translation.reshape(3,1) ]), jnp.array([0.0, 0.0, 0.0, 1.0])]
    )
vmf_jit = jax.jit(vmf)

def gaussian_vmf_cov(key, covar, concentration):
    translation = tfp.distributions.MultivariateNormalFullCovariance(jnp.zeros(3), covar).sample(seed=key)
    quat = tfp.distributions.VonMisesFisher(
        jnp.array([1.0, 0.0, 0.0, 0.0]), concentration
    ).sample(seed=key)
    rot_matrix =  quaternion_to_rotation_matrix(quat)
    return jnp.vstack(
        [jnp.hstack([rot_matrix, translation.reshape(3,1) ]), jnp.array([0.0, 0.0, 0.0, 1.0])]
    )

def gaussian_vmf(key, var, concentration):
    translation = tfp.distributions.MultivariateNormalDiag(jnp.zeros(3), jnp.ones(3) * var).sample(seed=key)
    quat = tfp.distributions.VonMisesFisher(
        jnp.array([1.0, 0.0, 0.0, 0.0]), concentration
    ).sample(seed=key)
    rot_matrix =  quaternion_to_rotation_matrix(quat)
    return jnp.vstack(
        [jnp.hstack([rot_matrix, translation.reshape(3,1) ]), jnp.array([0.0, 0.0, 0.0, 1.0])]
    )
    

def gaussian_vmf_sample(key, pose_mean, var, concentration):
    return pose_mean.dot(gaussian_vmf(key, var, concentration))

def gaussian_vmf_logpdf(pose, pose_mean, var, concentration):
    translation_prob = tfp.distributions.MultivariateNormalDiag(pose_mean[:3,3], jnp.ones(3) * var).log_prob(pose[:3,3])
    quat_mean = rotation_matrix_to_quaternion(pose_mean[:3,:3])
    quat = rotation_matrix_to_quaternion(pose[:3,:3])
    quat_prob = tfp.distributions.VonMisesFisher(
        quat_mean, concentration
    ).log_prob(quat)
    return translation_prob + quat_prob

def gaussian_vmf_mixture_sample(key, pose_means, log_weights, var, concentration):
    idx = tfp.distributions.Categorical(logits=log_weights).sample(seed=key)
    return gaussian_vmf_sample(key, pose_means[idx], var, concentration)

def gaussian_vmf_mixture_logpdf(key, pose, pose_means, log_weights, var, concentration):
    log_probs = jax.vmap(gaussian_vmf_logpdf, in_axes=(None, 0, None, None))(pose, pose_means, var, concentration)
    log_mixture_probabilites = log_probs + log_weights
    return logsumexp(log_mixture_probabilites)




def gaussian_vmf_logpdf(pose, pose_mean, var, concentration):
    translation_prob = tfp.distributions.MultivariateNormalDiag(pose_mean[:3,3], jnp.ones(3) * var).log_prob(pose[:3,3])
    quat_mean = rotation_matrix_to_quaternion(pose_mean[:3,:3])
    quat = rotation_matrix_to_quaternion(pose[:3,:3])
    quat_prob = tfp.distributions.VonMisesFisher(
        quat_mean, concentration
    ).log_prob(quat)
    return translation_prob + quat_prob


