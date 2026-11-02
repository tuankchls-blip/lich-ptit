from lichptit.cli import main


def test_help_runs():
    assert main([]) == 0


def test_check_du_lieu_that(capsys):
    assert main(["check"]) == 0
    assert "3 môn" in capsys.readouterr().out


def test_build_ghi_file_khong_in_token(data_dir, tmp_path, capsys):
    out = tmp_path / "_site"
    assert main(["--data", str(data_dir), "build", "--out", str(out), "--token", "abcXYZ123"]) == 0
    assert (out / "abcXYZ123" / "calendar.ics").exists()
    assert "abcXYZ123" not in capsys.readouterr().out


def test_build_thieu_token(data_dir, tmp_path, monkeypatch):
    monkeypatch.delenv("SITE_TOKEN", raising=False)
    assert main(["--data", str(data_dir), "build", "--out", str(tmp_path)]) == 2


def test_build_du_lieu_sai_khong_xuat(tmp_path, capsys):
    from conftest import write_data

    d = write_data(tmp_path / "d", tasks="- id: t1\n  title: x\n")
    out = tmp_path / "_site"
    assert main(["--data", str(d), "build", "--out", str(out), "--token", "t"]) == 1
    assert not (out / "t" / "calendar.ics").exists()
    assert "tasks.yaml:1:" in capsys.readouterr().err
