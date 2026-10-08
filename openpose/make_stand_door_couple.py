"""Standing bathroom couple OpenPose: junior left (leg up), Zhao right (penetrating)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_openpose import OUT, W, H, pack, make_hand, render_multi, save


def pose_stand_door_couple():
    # Face-to-face standing sex against wall.
    # LEFT = slim junior: back to wall, RIGHT leg lifted high.
    # RIGHT = Zhao: both feet down, supporting the raised thigh, hips locked.

    # --- JUNIOR (left, against wall) ---
    j_kps, j_r_wr, j_l_wr = pack(
        neck=(0.34, 0.17),
        look=(0.55, -0.10),
        scale=0.042,
        r_sh=(0.44, 0.19),
        l_sh=(0.24, 0.19),
        r_el=(0.48, 0.34),
        l_el=(0.40, 0.03),   # left elbow over crowns → nape from behind
        r_wr=(0.52, 0.42),   # right hand on Zhao's side/back
        l_wr=(0.56, 0.15),   # left hand on Zhao nape from behind
        r_hip=(0.42, 0.44),
        l_hip=(0.30, 0.45),
        r_kn=(0.78, 0.38),   # raised thigh almost horizontal, knee high-right
        l_kn=(0.30, 0.68),
        r_an=(0.88, 0.52),   # foot hanging
        l_an=(0.30, 0.93),
    )
    j_l_hand = make_hand(j_l_wr, toward=(8, 32), scale=26, curl=0.40)
    j_r_hand = make_hand(j_r_wr, toward=(28, 0), scale=26, curl=0.45)

    # --- ZHAO (right) ---
    z_kps, z_r_wr, z_l_wr = pack(
        neck=(0.58, 0.15),
        look=(-0.65, 0.15),
        scale=0.052,
        r_sh=(0.72, 0.18),
        l_sh=(0.48, 0.20),
        r_el=(0.54, 0.34),
        l_el=(0.66, 0.32),
        r_wr=(0.40, 0.36),   # right arm around junior's back
        l_wr=(0.74, 0.40),   # left hand under raised thigh near knee
        r_hip=(0.62, 0.46),
        l_hip=(0.52, 0.46),  # hips flush for penetration
        r_kn=(0.68, 0.70),
        l_kn=(0.50, 0.70),
        r_an=(0.70, 0.94),
        l_an=(0.48, 0.94),
    )
    z_l_hand = make_hand(z_l_wr, toward=(40, -15), scale=34, curl=0.30)
    z_r_hand = make_hand(z_r_wr, toward=(-36, 6), scale=30, curl=0.50)

    return [
        (j_kps, [j_r_hand, j_l_hand]),
        (z_kps, [z_r_hand, z_l_hand]),
    ]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    canvas = render_multi(pose_stand_door_couple())
    save("39_stand_door_couple_openpose.png", canvas)
    print(f"canvas {W}x{H}")


if __name__ == "__main__":
    main()
