"""Differentiable ProteinAE adapter with controllable decoder noise.

The external ProteinAE checkout and checkpoint remain read-only dependencies.
"""
import torch
from torch import nn


def load_proteinae(checkout, checkpoint, *, steps=3):
    """Load the known external ProteinAE implementation on CPU, without chdir.

    This uses Lightning's pickle-based loader for a trusted local AE checkpoint.
    No gate/training module from the old project is imported.
    """
    import sys
    from pathlib import Path
    checkout = Path(checkout).resolve()
    sys.path.insert(0, str(checkout))
    try:
        import hydra
        from proteinfoundation.proteinflow.proteinae import ProteinAE
        with hydra.initialize_config_dir(config_dir=str(checkout / "configs/experiment_config"),
                                         version_base=None):
            hydra.compose(config_name="inference_proteinae", return_hydra_config=True)
        ae = ProteinAE.load_from_checkpoint(str(Path(checkpoint).resolve()), strict=True,
                                           weights_only=False, map_location="cpu").eval()
    finally:
        sys.path.remove(str(checkout))
    for parameter in ae.parameters():
        parameter.requires_grad_(False)
    return DifferentiableDecoder(ae, n_steps=steps).eval()

class DifferentiableDecoder(nn.Module):
    """Wraps ProteinAE decoder for differentiable z → coords mapping.

    Uses Euler ODE integration with gradients flowing through each step.
    """
    def __init__(self, ae_model, n_steps=10):
        super().__init__()
        self.decoder = ae_model.decoder
        self.fm = ae_model.fm
        self.ae_model = ae_model
        if n_steps < 1:
            raise ValueError("decoder steps must be positive")
        self.n_steps = n_steps

        # Freeze decoder
        for p in self.decoder.parameters():
            p.requires_grad = False

        # Check parameterization
        self.target_pred = ae_model.cfg_exp.model.target_pred

    @torch.no_grad()
    def _sample_initial_noise(self, batch_size, n_atoms, device, generator):
        """Sample initial Gaussian noise for backbone atoms."""
        x = torch.randn(batch_size, n_atoms, 3, device=device, generator=generator) * self.fm.scale_ref
        return x

    def _nn_out_to_x_clean(self, nn_out, x_t, t):
        """Convert decoder output to clean coords prediction."""
        nn_pred = nn_out["coors_pred"]
        if self.target_pred == "x_1":
            return nn_pred
        elif self.target_pred == "v":
            t_ext = t[:, None, None]
            return x_t + (1.0 - t_ext) * nn_pred
        else:
            raise ValueError(f"Unknown target_pred: {self.target_pred}")

    def forward(self, z, mask, return_backbone=False, *, generator=None, noise=None):
        """Decode z to Ca coordinates with differentiable ODE.

        return_backbone: also return the full (B, N, 4, 3) backbone in
        Angstroms, atom order [N, CA, C, O], as (ca, backbone).

        The decoder operates in backbone mode (4 atoms per residue: N, Ca, C, O).
        x_t shape: (B, N*4, 3), coords_mask shape: (B, N*4).

        Args:
            z: (B, N, 8) predicted latent vectors
            mask: (B, N) bool mask
        Returns:
            ca_coords: (B, N, 3) predicted Ca coordinates in Angstroms
        """
        B, N, _ = z.shape
        device = z.device

        # Backbone mode: 4 atoms per residue
        n_atoms = N * 4
        coords_mask = mask.unsqueeze(-1).expand(-1, -1, 4).reshape(B, n_atoms)

        # Time schedule: uniform from 0 to 1
        ts = torch.linspace(0, 1, self.n_steps + 1, device=device)

        # Start from noise
        x = self._sample_initial_noise(B, n_atoms, device, generator) if noise is None else noise.clone()
        if x.shape != (B, n_atoms, 3) or not torch.isfinite(x).all():
            raise ValueError("decoder noise must have shape (B, 4L, 3) and be finite")

        for step in range(self.n_steps):
            t_val = ts[step]
            dt = ts[step + 1] - ts[step]
            t = t_val * torch.ones(B, device=device)

            batch_nn = {
                "x_t": x,
                "t": t,
                "mask": mask,
                "coords_mask": coords_mask,
                "single_repr": z,
            }

            # Forward through frozen decoder (gradients flow through z only)
            nn_out = self.decoder(batch_nn)
            x_clean = self._nn_out_to_x_clean(nn_out, x, t)

            # Euler step: v = (x_clean - x_t) / (1 - t), x_{t+dt} = x_t + v * dt
            v = (x_clean - x) / (1.0 - t_val + 1e-6)
            x = x + v * dt.item()

            # Zero out masked atoms
            x = x * coords_mask.unsqueeze(-1).float()

        # Extract Ca atoms (index 1 of each 4-atom group) and convert nm → Angstroms
        # Reshape to (B, N, 4, 3), take atom index 1
        x_backbone = x.reshape(B, N, 4, 3)
        ca_coords = x_backbone[:, :, 1, :] * 10.0

        if return_backbone:
            return ca_coords, x_backbone * 10.0
        return ca_coords
