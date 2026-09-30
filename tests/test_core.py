import cv2
import numpy as np

from zit.core import Zit


def make_zit(tmp_path, **kwargs):
    return Zit(input_video="", output_folder=str(tmp_path), interval=1, **kwargs)


def write_frames(folder, frames):
    for i, frame in enumerate(frames):
        cv2.imwrite(str(folder / f"frame_{i}.jpg"), frame)


def test_frame_match():
    assert Zit.frame_match("frame_120.jpg") == 120
    assert Zit.frame_match("frame_0.jpg") == 0
    assert Zit.frame_match("notes.txt") == -1


def test_filter_files_by_range(tmp_path):
    z = make_zit(tmp_path)
    files = ["frame_0.jpg", "frame_30.jpg", "frame_60.jpg", "frame_90.jpg"]
    assert z.filter_files_by_range(files, "frame_30.jpg", "frame_60.jpg") == [
        "frame_30.jpg",
        "frame_60.jpg",
    ]


def test_clear_folder_only_removes_frames(tmp_path):
    (tmp_path / "frame_0.jpg").write_bytes(b"x")
    (tmp_path / "frame_30.jpg").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("keep me")
    (tmp_path / "photo.jpg").write_bytes(b"keep me")

    Zit.clear_folder(str(tmp_path))

    assert sorted(p.name for p in tmp_path.iterdir()) == ["notes.txt", "photo.jpg"]


def test_clear_folder_missing_folder(tmp_path):
    Zit.clear_folder(str(tmp_path / "does-not-exist"))


def test_apply_composite_copies_only_distinct_pixels(tmp_path):
    z = make_zit(tmp_path, composite_epsilon=20.0, noise_delta=50.0)
    bg = np.zeros((10, 10, 3), dtype=np.uint8)
    ol = np.zeros((10, 10, 3), dtype=np.uint8)
    ol[2:4, 2:4] = 255

    result = z._apply_composite(bg.copy(), ol)

    assert (result[2:4, 2:4] == 255).all()
    assert result.sum() == 255 * 3 * 4


def test_capture_frames(tmp_path):
    video_path = str(tmp_path / "clip.avi")
    writer = cv2.VideoWriter(
        video_path, cv2.VideoWriter_fourcc(*"MJPG"), 10, (32, 32)
    )
    for _ in range(25):
        writer.write(np.full((32, 32, 3), 128, dtype=np.uint8))
    writer.release()

    out = tmp_path / "frames"
    Zit(input_video=video_path, output_folder=str(out), interval=1).capture_frames()

    assert sorted(p.name for p in out.iterdir()) == [
        "frame_0.jpg",
        "frame_10.jpg",
        "frame_20.jpg",
    ]


def test_entity_composite_captures_moving_object(tmp_path):
    z = make_zit(tmp_path, composite_epsilon=16.0, noise_delta=20.0)
    frames = []
    for i in range(10):
        frame = np.full((64, 128, 3), 40, dtype=np.uint8)
        # Step farther than the square is wide so no pixel is covered twice
        # and MOG2 can't absorb the square into the background.
        x = 5 + i * 12
        frame[25:35, x : x + 10] = 220
        frames.append(frame)
    write_frames(tmp_path, frames)

    out_file = str(tmp_path / "out.png")
    z.composite_from_frames(out_file, use_entities=True)
    result = cv2.imread(out_file)

    assert result is not None
    # The moving square's trail is drawn onto the composite...
    assert result[25:35].max() > 180
    # ...while rows it never touched stay background.
    assert result[:15].max() < 80
